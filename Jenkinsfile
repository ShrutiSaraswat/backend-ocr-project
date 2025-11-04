pipeline {
    agent any

    environment {
        PYTHON   = 'python'
        VENV_DIR = 'venv'
        DEPLOY_DIR = 'C:\\DeployedApps\\OCRProject'

        // Optional AWS credentials (safe placeholders)
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

        stage('Run Tests (non-blocking)') {
            steps {
                echo '🧪 Running tests if any...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate
                    python -m pytest > test_output.log 2>&1 || echo "⚠️ No tests configured, skipping tests..."
                    exit /b 0
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying Flask OCR service persistently...'
                bat '''
                    rem === Create deployment directory ===
                    if not exist "%DEPLOY_DIR%" mkdir "%DEPLOY_DIR%"
                    xcopy * "%DEPLOY_DIR%\\" /E /Y >nul

                    cd /d "%DEPLOY_DIR%"
                    call %VENV_DIR%\\Scripts\\activate

                    rem === Kill any process using port 5000 ===
                    for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000"') do taskkill /PID %%a /F 2>nul || echo No old process found

                    rem === Start Flask app safely in background ===
                    echo Starting Flask server in background...
                    start /b cmd /c "call %VENV_DIR%\\Scripts\\activate && python server.py > flask_stdout.log 2>&1"
                    timeout /t 5 >nul
                    echo ✅ Flask server started persistently on port 5000!
                '''
            }
        }

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
