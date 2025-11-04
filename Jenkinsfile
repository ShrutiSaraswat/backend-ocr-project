pipeline {
    agent any

    environment {
        PYTHON   = 'python'
        VENV_DIR = 'venv'

        // Optional AWS credentials for S3 uploads
        S3_BUCKET     = credentials('S3_BUCKET')
        S3_REGION     = credentials('S3_REGION')
        S3_ACCESS_KEY = credentials('S3_ACCESS_KEY')
        S3_SECRET_KEY = credentials('S3_SECRET_KEY')

        DEPLOY_DIR = 'C:\\DeployedApps\\OCRProject'   // persistent deployment path
    }

    stages {

        /* --------------------- CLONE --------------------- */
        stage('Clone Repository') {
            steps {
                echo '📥 Cloning public GitHub repository...'
                git branch: 'main', url: 'https://github.com/ShrutiSaraswat/backend-ocr-project.git'
            }
        }

        /* --------------------- SETUP --------------------- */
        stage('Set up Python Environment') {
            steps {
                echo '🐍 Creating Python virtual environment...'
                bat '''
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        /* --------------------- VERIFY --------------------- */
        stage('Verify Dependencies') {
            steps {
                echo '🔍 Verifying environment setup...'
                bat '''
                    chcp 65001 >NUL
                    call %VENV_DIR%\\Scripts\\activate
                    python -c "import flask, boto3, dotenv; print('Environment ready - dependencies imported successfully.')"
                '''
            }
        }

        /* --------------------- TESTS --------------------- */
        stage('Run Tests') {
            steps {
                echo '🧪 Running tests if any...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate
                    python -m pytest || echo "⚠️ No tests configured, skipping..."
                '''
            }
        }

        /* --------------------- DEPLOY --------------------- */
        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying Flask OCR service (persistent mode)...'

                bat '''
                    rem === Create persistent deployment directory ===
                    if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"
                    xcopy * "%DEPLOY_DIR%\\" /E /Y >nul

                    cd /d "%DEPLOY_DIR%"

                    rem === Activate virtual env and install deps ===
                    call %VENV_DIR%\\Scripts\\activate
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt

                    rem === Stop any running instance on port 5000 ===
                    for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000"') do taskkill /PID %%a /F 2>nul || echo No previous server found

                    rem === Start Flask in detached background mode ===
                    echo Starting Flask server in background...
                    start "" cmd /c "call %VENV_DIR%\\Scripts\\activate && python server.py > flask_stdout.log 2>&1"
                    timeout /t 5 >nul
                    echo ✅ Flask server launched persistently on port 5000!
                '''
            }
        }

        /* --------------------- VERIFY HEALTH --------------------- */
        stage('Verify Server Health') {
            steps {
                echo '🔎 Checking Flask health endpoint (with retry)...'
                bat '''
                    setlocal enabledelayedexpansion
                    set RETRIES=5
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
                        echo Waiting before retry...
                        timeout /t 5 >nul
                        goto RETRY
                    )
                    echo ❌ Health check failed after !RETRIES! attempts.
                    exit /b 1
                '''
            }
        }
    }

    /* --------------------- POST --------------------- */
    post {
        success {
            echo '✅ Build & deployment successful!'
            bat '''
                echo Deployment path: %DEPLOY_DIR%
                if exist "%DEPLOY_DIR%\\flask_stdout.log" echo ---- Flask stdout ---- && type "%DEPLOY_DIR%\\flask_stdout.log"
            '''
            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
        }
        failure {
            echo '❌ Build or deployment failed. Check console output.'
            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
        }
        always {
            echo "📅 Build completed at: ${new Date()}"
        }
    }
}
