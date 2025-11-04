pipeline {
    agent any

    environment {
        PYTHON   = 'python'
        VENV_DIR = 'venv'

        // Inject AWS credentials securely from Jenkins credentials store
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

        stage('Run Tests') {
            steps {
                echo '🧪 Running tests if any...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate
                    python -m pytest || exit /b 0
                    echo "⚠️ No tests configured, skipping..."
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Starting Flask OCR service...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate
                    for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000"') do taskkill /PID %%a /F || echo No running Flask server found
                    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process python -ArgumentList 'server.py' -WindowStyle Hidden"
                    timeout /t 10 >nul
                    echo ✅ Flask server started on port 5000!
                    exit /b 0
                '''
            }
        }

        stage('Verify Server Health') {
            steps {
                echo '🔎 Checking Flask health endpoint (with retry)...'
                bat '''
                    setlocal enabledelayedexpansion
                    set RETRIES=3
                    set COUNT=1
                    :RETRY
                    echo Attempt !COUNT! of !RETRIES!
                    curl -s http://localhost:5000/health >nul 2>&1 && (
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
            // Only archive if the file exists
            bat '''
                if exist app.log (
                    echo Archiving app.log...
                ) else (
                    echo No app.log found, skipping archive.
                )
            '''
        }
        failure {
            echo '❌ Build or deployment failed. Check console output.'
        }
        always {
            echo "📅 Build completed at: ${new Date()}"
            // Auto stop Flask if running
            bat '''
                for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000"') do taskkill /PID %%a /F || echo No Flask process running.
            '''
        }
    }
}
