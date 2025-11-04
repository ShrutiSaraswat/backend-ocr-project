pipeline {
    agent any

    environment {
        PYTHON      = 'python'
        DEPLOY_DIR  = 'C:\\DeployedApps\\OCRProject'
        SERVICE_NAME = 'OCRFlask'   // if C:\nssm\nssm.exe exists we install a Windows service with this name

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

        stage('Install into DEPLOY_DIR') {
            steps {
                echo '📦 Preparing deployment directory and virtualenv...'
                bat '''
                    rem === Create deployment directory and copy sources ===
                    if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"
                    xcopy * "%DEPLOY_DIR%\\" /E /Y >nul

                    rem === Create or reuse venv inside DEPLOY_DIR ===
                    if not exist "%DEPLOY_DIR%\\venv\\Scripts\\python.exe" (
                        %PYTHON% -m venv "%DEPLOY_DIR%\\venv"
                    )

                    rem === Install requirements in the deploy venv (plus waitress) ===
                    cd /d "%DEPLOY_DIR%"
                    call "%DEPLOY_DIR%\\venv\\Scripts\\activate"
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install waitress
                '''
            }
        }

        stage('Verify environment') {
            steps {
                echo '🔍 Verifying imports in deploy venv...'
                bat '''
                    cd /d "%DEPLOY_DIR%"
                    call "%DEPLOY_DIR%\\venv\\Scripts\\activate"
                    python -c "import flask, waitress, boto3; print('Environment OK')"
                '''
            }
        }

        stage('Open firewall (idempotent)') {
            steps {
                bat '''
                    powershell -NoProfile -Command "if (-not (Get-NetFirewallRule -DisplayName 'OCR Flask 5000' -ErrorAction SilentlyContinue)) { New-NetFirewallRule -DisplayName 'OCR Flask 5000' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5000 | Out-Null }"
                '''
            }
        }

        stage('Deploy - service or detached process') {
            steps {
                echo '🚀 Deploying with Waitress...'
                bat '''
                    cd /d "%DEPLOY_DIR%"
                    setlocal enabledelayedexpansion

                    rem === Stop old instance by PID if present ===
                    if exist "%DEPLOY_DIR%\\flask.pid" (
                      for /f %%p in (%DEPLOY_DIR%\\flask.pid) do taskkill /PID %%p /F 1>nul 2>&1
                      del "%DEPLOY_DIR%\\flask.pid" 1>nul 2>&1
                    )

                    rem === Kill anything listening on 5000 (safety) ===
                    for /F "tokens=5" %%a in ('netstat -ano ^| find ":5000" ^| find "LISTENING"') do taskkill /PID %%a /F 1>nul 2>&1

                    rem === Clear previous logs ===
                    del "%DEPLOY_DIR%\\flask_out.log" 1>nul 2>&1
                    del "%DEPLOY_DIR%\\flask_err.log" 1>nul 2>&1

                    set NSSM=C:\\nssm\\nssm.exe
                    set SVC=%SERVICE_NAME%

                    if exist "!NSSM!" (
                      echo Using NSSM Windows service...
                      "!NSSM!" stop  "!SVC!" 1>nul 2>&1
                      "!NSSM!" remove "!SVC!" confirm 1>nul 2>&1

                      "!NSSM!" install "!SVC!" "%DEPLOY_DIR%\\venv\\Scripts\\python.exe" "-m waitress --host=0.0.0.0 --port=5000 server:app"
                      "!NSSM!" set "!SVC!" AppDirectory "%DEPLOY_DIR%"
                      "!NSSM!" set "!SVC!" AppStdout   "%DEPLOY_DIR%\\flask_out.log"
                      "!NSSM!" set "!SVC!" AppStderr   "%DEPLOY_DIR%\\flask_err.log"
                      "!NSSM!" set "!SVC!" Start SERVICE_AUTO_START
                      "!NSSM!" set "!SVC!" AppRestartDelay 5000
                      "!NSSM!" start "!SVC!"
                    ) else (
                      echo NSSM not found - starting detached process with Waitress...
                      powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                        "$p = Start-Process -FilePath '%DEPLOY_DIR%\\venv\\Scripts\\python.exe' -ArgumentList '-m waitress --host=0.0.0.0 --port=5000 server:app' -WorkingDirectory '%DEPLOY_DIR%' -WindowStyle Hidden -PassThru -RedirectStandardOutput '%DEPLOY_DIR%\\flask_out.log' -RedirectStandardError '%DEPLOY_DIR%\\flask_err.log'; Set-Content -Path '%DEPLOY_DIR%\\flask.pid' -Value $p.Id"
                      powershell -NoProfile -Command "Start-Sleep -Seconds 3"
                    )

                    endlocal
                '''
            }
        }

        stage('Health check') {
            steps {
                echo '🔎 Checking health endpoint with retries...'
                bat '''
                    setlocal
                    for /l %%i in (1,1,15) do (
                        echo Attempt %%i of 15
                        curl -s -o NUL -w "%%{http_code}" http://127.0.0.1:5000/health > status.txt 2>NUL
                        set /p CODE=<status.txt
                        del /f /q status.txt >NUL 2>&1
                        if "!CODE!"=="200" goto :ok
                        powershell -NoProfile -Command "Start-Sleep -Seconds 2"
                    )
                    echo ❌ Health check failed
                    exit /b 1
                    :ok
                    echo ✅ Health OK
                    endlocal
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
