# server.py
# Upload PDF -> (optional decrypt w/ qpdf) -> ocrmypdf -> upload to S3 -> public URL
# Improvements made:
# - Pre-detect encryption with qpdf --show-encryption
# - If no password and encrypted => 400 with clear message
# - If password provided => decrypt first, then OCR
# - Encryption checks prioritized before PDF/A fallback
# - Keeps Tagged PDF auto-retry (--force-ocr) and PDF/A -> PDF fallback
import os
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Tesseract-OCR"

import os
import uuid
import time
import logging
import tempfile
import subprocess
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import boto3
import shutil

# ---------- logging ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ocr-server")

# ---------- env ----------
load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

if not all([S3_BUCKET, S3_REGION, S3_ACCESS_KEY, S3_SECRET_KEY]):
    raise RuntimeError("Missing S3 env vars: S3_BUCKET, S3_REGION, S3_ACCESS_KEY, S3_SECRET_KEY")

# ---------- folders ----------
BASE_TMP = tempfile.gettempdir()
UPLOAD_FOLDER = os.path.join(BASE_TMP, "ocr_uploads")
OUTPUT_FOLDER = os.path.join(BASE_TMP, "ocr_outputs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------- flask ----------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ---------- s3 ----------
s3_client = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
)

# ---------- helpers ----------
def which_any(*names) -> str | None:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None

def check_dependencies() -> dict:
    return {
        "ocrmypdf": which_any("ocrmypdf"),
        "tesseract": which_any("tesseract"),
        "qpdf": which_any("qpdf"),
        "ghostscript": which_any("gswin64c", "gswin32c", "gs"),  # Windows/Linux/Mac
    }

def require_deps(or_pdfa: bool):
    deps = check_dependencies()
    missing = []
    if not deps["ocrmypdf"]:
        missing.append("ocrmypdf")
    if not deps["tesseract"]:
        missing.append("tesseract")
    if not deps["qpdf"]:
        missing.append("qpdf")
    if or_pdfa and not deps["ghostscript"]:
        missing.append("ghostscript (gswin64c/gs)")
    if missing:
        raise RuntimeError(
            "Missing dependencies: "
            + ", ".join(missing)
            + ". On Windows (Admin PowerShell): choco install -y tesseract ghostscript qpdf. "
              "Ensure they are on PATH and restart the terminal."
        )

def _bool(v: str | None, default=False) -> bool:
    if v is None:
        return default
    return str(v).strip().lower() in ("true", "1", "yes", "y", "on")

def _safe_output_type(v: str | None) -> str:
    return "pdfa" if str(v or "").lower() == "pdfa" else "pdf"

def _build_ocr_args(input_path: str, output_path: str, **opts) -> list[str]:
    languages = opts.get("languages", "eng")
    output_format = _safe_output_type(opts.get("output_format", "pdfa"))
    optimize_level = str(opts.get("optimize_level", "0"))
    deskew = _bool(opts.get("deskew"), False)
    fast_web_view = _bool(opts.get("fast_web_view"), False)
    rotate_pages = _bool(opts.get("rotate_pages"), False)
    skip_text = _bool(opts.get("skip_text"), False)
    redo_ocr = _bool(opts.get("redo_ocr"), False)
    force_ocr = _bool(opts.get("force_ocr"), False)
    invalidate = _bool(opts.get("invalidate_digital_signatures"), False)
    jobs = int(opts.get("jobs", 20))

    args = [
        "ocrmypdf",
        "--output-type", output_format,
        "--jobs", str(jobs),
        "-l", languages,
    ]
    if deskew:
        args.append("--deskew")
    if fast_web_view:
        args.append("--fast-web-view")
    if rotate_pages:
        args.append("--rotate-pages")
    if skip_text:
        args.append("--skip-text")
    if redo_ocr:
        args.append("--redo-ocr")
    if force_ocr:
        args.append("--force-ocr")
    if optimize_level in {"0", "1", "2", "3"}:
        args.extend(["--optimize", optimize_level])
    if invalidate:
        args.append("--invalidate-digital-signatures")

    args.extend([input_path, output_path])
    return args

def _run_ocr(input_path: str, output_path: str, **opts):
    output_format = _safe_output_type(opts.get("output_format", "pdfa"))
    require_deps(or_pdfa=(output_format == "pdfa"))

    args = _build_ocr_args(input_path, output_path, **opts)
    logger.info("Running ocrmypdf: %s", " ".join(args))

    proc = subprocess.run(args, check=False, timeout=int(opts.get("timeout", 600)), capture_output=True, text=True)
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, args, output=proc.stdout, stderr=proc.stderr)
    return True

def _upload_to_s3(local_path: str, key: str) -> str:
    s3_client.upload_file(
        local_path,
        S3_BUCKET,
        key,
        ExtraArgs={"ACL": "public-read", "ContentType": "application/pdf"},
    )
    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"

def _decrypt_with_qpdf(input_path: str, password: str) -> str:
    dec_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_decrypted.pdf")
    cmd = ["qpdf", f"--password={password}", "--decrypt", input_path, dec_path]
    logger.info("Decrypting with qpdf")
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"qpdf failed to decrypt PDF. stderr: {proc.stderr.strip()}")
    return dec_path

def _is_encrypted(input_path: str) -> bool:
    q = which_any("qpdf")
    if not q:
        # If qpdf is not present (shouldn't happen due to require_deps) assume not encrypted to avoid false positives
        return False
    # qpdf --show-encryption prints "no encryption" when not encrypted
    proc = subprocess.run([q, "--show-encryption", input_path], check=False, capture_output=True, text=True)
    output = (proc.stdout or "") + " " + (proc.stderr or "")
    low = output.lower()
    if "no encryption" in low:
        return False
    # Anything that mentions encryption info likely means it's encrypted
    return "encryption" in low or "aes" in low or "r =" in low or "key length" in low

# ---------- routes ----------
@app.get("/health")
def health():
    return jsonify({"ok": True, "time": datetime.utcnow().isoformat() + "Z", "deps": check_dependencies()})

@app.post("/ocr")
def ocr_pdf():
    if "file" not in request.files:
        return jsonify({"error": "Missing PDF file (field name: file)"}), 400

    f = request.files["file"]
    if not f or f.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not (f.mimetype == "application/pdf" or f.filename.lower().endswith(".pdf")):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    unique = str(uuid.uuid4())
    safe_name = secure_filename(f.filename)
    base, _ext = os.path.splitext(safe_name)
    ts = int(time.time() * 1000)
    in_path = os.path.join(UPLOAD_FOLDER, f"{ts}_{safe_name}")
    out_name = f"{base}_ocr.pdf"
    out_path = os.path.join(OUTPUT_FOLDER, f"{ts}_{out_name}")

    form = request.form or {}
    pdf_password = form.get("pdf_password") or None
    user_opts = {
        "languages": form.get("languages", "eng"),
        "output_format": form.get("output_format", "pdfa"),
        "optimize_level": form.get("optimize_level", "0"),
        "deskew": form.get("deskew", "false"),
        "fast_web_view": form.get("fast_web_view", "false"),
        "rotate_pages": form.get("rotate_pages", "false"),
        "skip_text": form.get("skip_text", "false"),
        "redo_ocr": form.get("redo_ocr", "false"),
        "force_ocr": form.get("force_ocr", "false"),
        "invalidate_digital_signatures": form.get("invalidate_digital_signatures", "false"),
        "jobs": form.get("jobs", "4"),
        "timeout": form.get("timeout", "600"),
    }

    decrypt_path = None
    try:
        f.save(in_path)

        # (0) Preflight: encryption detection before OCR
        if _is_encrypted(in_path):
            if not pdf_password:
                return jsonify({
                    "error": "PDF appears to be encrypted. Provide pdf_password or decrypt before uploading."
                }), 400
            try:
                decrypt_path = _decrypt_with_qpdf(in_path, pdf_password)
                source_path = decrypt_path
            except Exception as de:
                return jsonify({"error": "Failed to decrypt PDF", "details": str(de)}), 400
        else:
            source_path = in_path

        # (1) First OCR attempt
        try:
            _run_ocr(source_path, out_path, **user_opts)

        except subprocess.CalledProcessError as e1:
            stderr1 = (e1.stderr or "") + " " + (e1.output or "")
            low1 = stderr1.lower()

            # Prefer clear encryption message if we somehow missed it
            if "encryptedpdferror" in low1 or "encryp" in low1:
                return jsonify({
                    "error": "PDF appears to be encrypted. Provide pdf_password or decrypt before uploading.",
                    "stderr": e1.stderr,
                    "code": e1.returncode
                }), 400

            # Already-text/Tagged → retry with --force-ocr if not already set
            if ("taggedpdferror" in low1) or ("tagged pdf" in low1) or ("already has a text layer" in low1):
                logger.info("Detected Tagged/already-text PDF; retrying with --force-ocr")
                retry_force = dict(user_opts)
                retry_force["skip_text"] = "false"
                retry_force["redo_ocr"] = "false"
                retry_force["force_ocr"] = "true"
                _run_ocr(source_path, out_path, **retry_force)
            # PDF/A conversion issues → retry as regular PDF
            elif user_opts.get("output_format", "pdfa").lower() == "pdfa":
                logger.info("PDF/A failed; retrying with output_format=pdf")
                retry_pdf = dict(user_opts)
                retry_pdf["output_format"] = "pdf"
                _run_ocr(source_path, out_path, **retry_pdf)
            else:
                # Unknown failure
                raise

        # (2) Upload result
        s3_key = f"ocr_outputs/{unique}/{out_name}"
        url = _upload_to_s3(out_path, s3_key)
        return jsonify({"url": url})

    except RuntimeError as e:
        logger.exception("Preflight/dependency/decrypt error")
        return jsonify({"error": str(e)}), 500
    except subprocess.TimeoutExpired:
        logger.exception("OCR timed out")
        return jsonify({"error": "OCR timed out"}), 504
    except subprocess.CalledProcessError as e:
        logger.exception("ocrmypdf failed")
        return jsonify({"error": "ocrmypdf failed", "stderr": e.stderr, "stdout": e.output, "code": e.returncode}), 500
    except FileNotFoundError:
        logger.exception("ocrmypdf not found")
        return jsonify({"error": "ocrmypdf not found on server PATH. Install it and restart."}), 500
    except Exception as e:
        logger.exception("Unexpected error")
        return jsonify({"error": "OCR processing failed", "details": str(e)}), 500
    finally:
        # Cleanup temp files
        for p in [in_path, out_path, decrypt_path]:
            if not p:
                continue
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    logger.info("Starting OCR service on port %d", port)
    app.run(host="0.0.0.0", port=port)
