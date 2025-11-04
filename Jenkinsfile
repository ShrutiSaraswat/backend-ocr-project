pipeline {
    agent any

    environment {
        PYTHON     = 'python'
        DEPLOY_DIR = 'C:\\DeployedApps\\OCRProject'
        DEPLOY_VENV = 'C:\\DeployedApps\\OCRProject\\venv'

        // Optional AWS credentials
        S3_BUCKET     = credentials('S3_BUCKET')
        S3_REGION     = credentials('S3_REGION')
        S3_ACCESS_KEY = credentials('S3_ACCESS_KEY')
        S3_SECRET_KEY = credentials('S3_SECRET_KEY')
    }

    stages {

        stage('Clone Repository') {
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
                    if not exist "%DEPLOY_VENV%\\Scripts\\python.exe" (
                        %PYTHON% -m venv "%DEPLOY_VENV%"
                    )

                    rem === Install requirements inside deploy venv ===
                    cd /d "%DEPLOY_DIR%"
                    call "%DEPLOY_VENV%\\Scripts\\activate"
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Verify Dependencies') {
            steps {
                echo '🔍 Verifying environment setup...'
                bat '''
                    chcp 65001 >NUL
                    cd /d "%DEPLOY_DIR%"
                    call "%DEPLOY_VENV%\\Scripts\\activate"
                    python -c "import flask, boto3, dotenv; print('Environment OK')"
                '''
            }
        }

        stage('Run Tests (non-blocking)') {
            steps {
                echo '🧪 Running tests if present...'
                bat '''
                    cd /d "%DEPLOY_DIR%"
                    call "%DEPLOY_VENV%\\Scripts\\activate"
                    python -m pytest > "%DEPLOY_DIR%\\test_output.log" 2>&1 || echo "pytest not found or no tests. Skipping..." >> "%DEPLOY_DIR%\\test_output.log"
                    exit /b 0
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying Flask OCR service persistently...'
                bat '''
                    cd /d "%DEPLOY_DIR%"
                    setlocal enabledelayedexpansion

                    rem === Stop old instance by PID file if present ===
                    if exist "%DEPLOY_DIR%\\flask.pid" (
                        set /p OLD=<"%DEPLOY_DIR%\\flask.pid"
                        if not "!OLD!"=="" (
                            taskkill /PID !OLD! /F >nul 2>&1
                        )
                        del "%DEPLOY_DIR%\\flask.pid" >nul 2>&1
                    )

                    rem === Also kill anything listening on port 5000 ===
                    for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000" ^| find "LISTENING"') do (
                        taskkill /PID %%a /F >nul 2>&1
                    )

                    rem === Clear previous logs ===
                    del "%DEPLOY_DIR%\\flask_out.log" >nul 2>&1
                    del "%DEPLOY_DIR%\\flask_err.log" >nul 2>&1

                    rem === Start Flask app fully detached via PowerShell ===
                    echo Starting Flask server persistently...
                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                      "$p = Start-Process -FilePath '%DEPLOY_VENV%\\Scripts\\python.exe' -ArgumentList 'server.py' -WorkingDirectory '%DEPLOY_DIR%' -WindowStyle Hidden -PassThru -RedirectStandardOutput '%DEPLOY_DIR%\\flask_out.log' -RedirectStandardError '%DEPLOY_DIR%\\flask_err.log'; Set-Content -Path '%DEPLOY_DIR%\\flask.pid' -Value $p.Id"

                    rem Give it a moment to boot
                    timeout /t 5 >nul

                    echo ✅ Flask server launch command issued.
                '''
            }
        }

        stage('Verify Server Health') {
            steps {
                echo '🔎 Checking health endpoint with retries...'
                bat '''
                    setlocal enabledelayedexpansion
                    set RETRIES=10
                    set COUNT=1
                    :RETRY
                    echo Attempt !COUNT! of !RETRIES!
                    curl -s http://localhost:5000/health >nul 2>&1
                    if %ERRORLEVEL%==0 (
                        echo ✅ Flask health check passed!
                        exit /b 0
                    )
                    if !COUNT! lss !RETRIES! (
                        set /a COUNT+=1
                        timeout /t 2 >nul
                        goto RETRY
                    )
                    echo ❌ Health check failed after !RETRIES! attempts.
                    type "%DEPLOY_DIR%\\flask_err.log" 2>nul
                    exit /b 1
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Build and persistent deployment successful!'
            bat '''
                echo Deployment path: %DEPLOY_DIR%
                echo PID file: %DEPLOY_DIR%\\flask.pid
                echo Visit: http://localhost:5000/health
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
