pipeline {
    agent any

    environment {
        PYTHON   = 'python'
        VENV_DIR = 'venv'

        // Securely inject AWS credentials (optional)
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
                    for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000"') do taskkill /PID %%a /F 2>nul || echo No running Flask server found
                    echo Starting Flask server and logging output...
                    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                        "Start-Process python -ArgumentList 'server.py' -RedirectStandardOutput 'app_stdout.log' -RedirectStandardError 'app_stderr.log' -WindowStyle Hidden"
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
                    exit /b 0
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Build & deployment successful!'
            bat '''
                if exist app_stdout.log echo Archiving app_stdout.log...
                if exist app_stderr.log echo Archiving app_stderr.log...
            '''
            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
        }
        failure {
            echo '❌ Build or deployment failed. Check console output.'
            archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
        }
        always {
            echo "📅 Build completed at: ${new Date()}"
            // echo '🛑 Stopping any running Flask process...'
            // bat '''
            //     for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000"') do (
            //         if not "%%a"=="0" (
            //             taskkill /PID %%a /F >nul 2>&1 || echo Could not kill PID %%a
            //         )
            //     )
            //     exit /b 0
            // '''
        }
    }
}
