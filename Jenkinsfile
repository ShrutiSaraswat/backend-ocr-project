pipeline {
    agent any

    environment {
        PYTHON       = 'python'
        DEPLOY_DIR   = 'C:\\DeployedApps\\OCRProject'
        VENV_DIR     = 'C:\\DeployedApps\\OCRProject\\.venv'
        SERVICE_NAME = 'OCRFlask'

        // Optional AWS credentials
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
                    robocopy . "%DEPLOY_DIR%" /MIR /XD .git venv .venv __pycache__ .pytest_cache /XF *.pyc *.pyo >nul
                    set RC=%ERRORLEVEL%
                    rem robocopy returns 0..3 for success
                    if %RC% GTR 3 exit /b %RC%
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
                echo '📦 Installing Python deps into the correct venv...'
                bat '''
                    cd /d "%DEPLOY_DIR%"
                    "%VENV_DIR%\\Scripts\\python.exe" -m pip install --upgrade pip
                    "%VENV_DIR%\\Scripts\\python.exe" -m pip install -r requirements.txt
                    "%VENV_DIR%\\Scripts\\python.exe" -m pip install waitress
                    "%VENV_DIR%\\Scripts\\python.exe" -c "import sys, flask, waitress; print('Using:', sys.executable)"
                '''
            }
        }

        stage('Open firewall for 5000') {
            steps {
                bat '''
                    powershell -NoProfile -Command "if (-not (Get-NetFirewallRule -DisplayName 'OCR Flask 5000' -ErrorAction SilentlyContinue)) { New-NetFirewallRule -DisplayName 'OCR Flask 5000' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5000 | Out-Null }"
                '''
            }
        }

        stage('Deploy - service or detached process') {
            steps {
                echo '🚀 Starting Waitress server...'
                bat '''
                    cd /d "%DEPLOY_DIR%"
                    setlocal enabledelayedexpansion

                    rem Stop prior PID if present
                    if exist "%DEPLOY_DIR%\\flask.pid" (
                      for /f %%p in (%DEPLOY_DIR%\\flask.pid) do taskkill /PID %%p /F 1>nul 2>&1
                      del "%DEPLOY_DIR%\\flask.pid" 1>nul 2>&1
                    )

                    rem Kill any listener on 5000
                    for /F "tokens=5" %%a in ('netstat -ano ^| find ":5000" ^| find "LISTENING"') do taskkill /PID %%a /F 1>nul 2>&1

                    rem Clear old logs
                    del "%DEPLOY_DIR%\\flask_out.log"  1>nul 2>&1
                    del "%DEPLOY_DIR%\\flask_err.log"  1>nul 2>&1

                    set NSSM=C:\\nssm\\nssm.exe
                    set SVC=%SERVICE_NAME%

                    if exist "!NSSM!" (
                      echo Using NSSM service...
                      "!NSSM!" stop  "!SVC!"  1>nul 2>&1
                      "!NSSM!" remove "!SVC!" confirm 1>nul 2>&1
                      "!NSSM!" install "!SVC!" "%VENV_DIR%\\Scripts\\python.exe" "-m waitress --host=0.0.0.0 --port=5000 server:app"
                      "!NSSM!" set "!SVC!" AppDirectory "%DEPLOY_DIR%"
                      "!NSSM!" set "!SVC!" AppStdout   "%DEPLOY_DIR%\\flask_out.log"
                      "!NSSM!" set "!SVC!" AppStderr   "%DEPLOY_DIR%\\flask_err.log"
                      "!NSSM!" set "!SVC!" Start SERVICE_AUTO_START
                      "!NSSM!" set "!SVC!" AppRestartDelay 5000
                      "!NSSM!" start "!SVC!"
                    ) else {
                      echo NSSM not found - starting detached process...
                      powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                        "$p = Start-Process -FilePath '%VENV_DIR%\\Scripts\\python.exe' -ArgumentList '-m waitress --host=0.0.0.0 --port=5000 server:app' -WorkingDirectory '%DEPLOY_DIR%' -WindowStyle Hidden -PassThru -RedirectStandardOutput '%DEPLOY_DIR%\\flask_out.log' -RedirectStandardError '%DEPLOY_DIR%\\flask_err.log'; Set-Content -Path '%DEPLOY_DIR%\\flask.pid' -Value $p.Id"
                      powershell -NoProfile -Command "Start-Sleep -Seconds 3"
                    }

                    endlocal
                '''
            }
        }

        stage('Health check') {
            steps {
                echo '🔎 Verifying /health via PowerShell...'
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
                echo Visit: http://127.0.0.1:5000/health
                echo ---- Last 30 lines of flask_out.log ----
                powershell -NoProfile -Command "if (Test-Path '%DEPLOY_DIR%\\flask_out.log') { Get-Content -Path '%DEPLOY_DIR%\\flask_out.log' -Tail 30 }"
                echo ---- Last 30 lines of flask_err.log ----
                powershell -NoProfile -Command "if (Test-Path '%DEPLOY_DIR%\\flask_err.log') { Get-Content -Path '%DEPLOY_DIR%\\flask_err.log' -Tail 30 }"
            '''
            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
        }
        failure {
            echo '❌ Build or deployment failed. See logs above.'
            bat '''
                echo ---- Last 60 lines of flask_err.log (if any) ----
                powershell -NoProfile -Command "if (Test-Path '%DEPLOY_DIR%\\flask_err.log') { Get-Content -Path '%DEPLOY_DIR%\\flask_err.log' -Tail 60 }"
            '''
            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
        }
        always {
            echo "📅 Build completed at: ${new Date()}"
        }
    }
}
