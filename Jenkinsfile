pipeline {
  agent any

  environment {
    PYTHON       = 'python'
    DEPLOY_DIR   = 'C:\\DeployedApps\\OCRProject'
    VENV_DIR     = 'C:\\DeployedApps\\OCRProject\\.venv'
    SERVICE_NAME = 'OCRFlask'
    NSSM_PATH    = 'C:\\nssm\\nssm.exe'

    // Optional AWS credentials (safe to leave as-is)
    S3_BUCKET     = credentials('S3_BUCKET')
    S3_REGION     = credentials('S3_REGION')
    S3_ACCESS_KEY = credentials('S3_ACCESS_KEY')
    S3_SECRET_KEY = credentials('S3_SECRET_KEY')
  }

  stages {

    stage('Checkout') {
      steps {
        echo '📥 Cloning public GitHub repository...'
        git branch: 'main', url: 'https://github.com/ShrutiSaraswat/backend-ocr-project.git'
      }
    }

    stage('Sync to DEPLOY_DIR (exclude venv)') {
      steps {
        echo '📦 Syncing sources into DEPLOY_DIR without any virtualenv...'
        bat '''
          if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"
          robocopy . "%DEPLOY_DIR%" /MIR ^
            /XD .git venv .venv __pycache__ .pytest_cache ^
            /XF *.pyc *.pyo *.log >nul

          rem ✅ Mark robocopy success if code < 8
          set RC=%ERRORLEVEL%
          if %RC% LSS 8 (exit /b 0) else (exit /b %RC%)
        '''
      }
    }

    stage('Create or reuse venv') {
      steps {
        echo '🐍 Ensuring deploy venv exists...'
        bat '''
          if not exist "%VENV_DIR%\\Scripts\\python.exe" (
            %PYTHON% -m venv "%VENV_DIR%"
          )
          "%VENV_DIR%\\Scripts\\python.exe" -V
        '''
      }
    }

    stage('Install requirements into deploy venv') {
      steps {
        echo '📦 Installing Python dependencies...'
        bat '''
          cd /d "%DEPLOY_DIR%"
          "%VENV_DIR%\\Scripts\\python.exe" -m pip install --upgrade pip
          "%VENV_DIR%\\Scripts\\python.exe" -m pip install -r requirements.txt
          "%VENV_DIR%\\Scripts\\python.exe" -m pip install waitress
          "%VENV_DIR%\\Scripts\\python.exe" -c "import flask, waitress; print('Flask + Waitress ready')"
        '''
      }
    }

    stage('Ensure NSSM installed') {
      steps {
        echo '🧰 Ensuring NSSM exists...'
        bat '''
          if not exist "C:\\nssm\\nssm.exe" (
            echo 🔽 Downloading NSSM...
            powershell -NoProfile -ExecutionPolicy Bypass -Command ^
              "$url='https://nssm.cc/release/nssm-2.24.zip';" ^
              "$zip='C:\\nssm.zip'; $out='C:\\nssm';" ^
              "Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing;" ^
              "Expand-Archive -Path $zip -DestinationPath $out -Force;" ^
              "Copy-Item 'C:\\nssm\\nssm-2.24\\win64\\nssm.exe' 'C:\\nssm\\nssm.exe' -Force;" ^
              "Remove-Item $zip -Force"
            echo ✅ NSSM installed to C:\\nssm\\nssm.exe
          ) else (
            echo 🟢 NSSM already present at C:\\nssm\\nssm.exe
          )
        '''
      }
    }

    stage('Open firewall for port 5000') {
      steps {
        bat '''
          powershell -NoProfile -Command "if (-not (Get-NetFirewallRule -DisplayName 'OCR Flask 5000' -ErrorAction SilentlyContinue)) { New-NetFirewallRule -DisplayName 'OCR Flask 5000' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5000 | Out-Null }"
        '''
      }
    }

    stage('Deploy as persistent Windows Service (NSSM)') {
      steps {
        echo '🚀 Installing/Restarting OCRFlask service via NSSM...'
        bat '''
          cd /d "%DEPLOY_DIR%"

          if not exist "%NSSM_PATH%" (
            echo ❌ NSSM not found at %NSSM_PATH%
            exit /b 1
          )

          echo 🧹 Stopping existing service if any...
          "%NSSM_PATH%" stop "%SERVICE_NAME%" 1>nul 2>&1
          "%NSSM_PATH%" remove "%SERVICE_NAME%" confirm 1>nul 2>&1

          echo ⚙️ Installing new service...
          "%NSSM_PATH%" install "%SERVICE_NAME%" "%VENV_DIR%\\Scripts\\python.exe" "-m waitress --host=0.0.0.0 --port=5000 server:app"
          "%NSSM_PATH%" set "%SERVICE_NAME%" AppDirectory "%DEPLOY_DIR%"
          "%NSSM_PATH%" set "%SERVICE_NAME%" AppStdout "%DEPLOY_DIR%\\flask_out.log"
          "%NSSM_PATH%" set "%SERVICE_NAME%" AppStderr "%DEPLOY_DIR%\\flask_err.log"
          "%NSSM_PATH%" set "%SERVICE_NAME%" Start SERVICE_AUTO_START
          "%NSSM_PATH%" set "%SERVICE_NAME%" AppRestartDelay 5000
          "%NSSM_PATH%" set "%SERVICE_NAME%" DisplayName "OCR Flask API Service"
          "%NSSM_PATH%" set "%SERVICE_NAME%" Description "Persistent Flask OCR API running on port 5000"

          echo ▶️ Starting service...
          "%NSSM_PATH%" start "%SERVICE_NAME%"
          powershell -NoProfile -Command "Start-Sleep -Seconds 5"

          sc query "%SERVICE_NAME%"
        '''
      }
    }

    stage('Health Check (persistent service)') {
      steps {
        echo '🔎 Verifying /health endpoint...'
        bat '''
          powershell -NoProfile -Command ^
            "$url='http://127.0.0.1:5000/health';" ^
            "for($i=1;$i -le 20;$i++){" ^
            "  try{ $r=Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){ Write-Output '✅ Health OK'; exit 0 } } catch { }" ^
            "  Write-Output ('Attempt ' + $i + ' not ready, retrying...'); Start-Sleep -Seconds 2" ^
            "}; Write-Output '❌ Health check failed'; exit 1"
        '''
      }
    }
  }

  post {
    success {
      echo '✅ Build and persistent deployment successful!'
      bat '''
        echo Deployment path: %DEPLOY_DIR%
        echo Service name: %SERVICE_NAME%
        echo Logs: %DEPLOY_DIR%\\flask_out.log / %DEPLOY_DIR%\\flask_err.log
        echo Visit: http://127.0.0.1:5000/health
        powershell -NoProfile -Command "if (Test-Path '%DEPLOY_DIR%\\flask_out.log') { Get-Content '%DEPLOY_DIR%\\flask_out.log' -Tail 30 }"
      '''
    }
    failure {
      echo '❌ Build or deployment failed. See logs above.'
      bat '''
        echo ---- Last 60 lines of flask_err.log (if any) ----
        powershell -NoProfile -Command "if (Test-Path '%DEPLOY_DIR%\\flask_err.log') { Get-Content '%DEPLOY_DIR%\\flask_err.log' -Tail 60 }"
      '''
    }
    always {
      echo "📅 Build completed at: ${new Date()}"
    }
  }
}
