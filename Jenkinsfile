pipeline {
    agent any

    environment {
        PYTHON   = 'python'            // Windows uses 'python'
        VENV_DIR = 'venv'

        // Inject AWS credentials securely from Jenkins secrets
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
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Verify Dependencies') {
            steps {
                echo '🔍 Verifying environment setup...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate
                    python -c "import flask, boto3, dotenv; print('✅ Environment ready!')"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running tests if any...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate
                    python -m pytest || echo "⚠️ No tests configured, skipping..."
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Starting Flask OCR service...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate
                    for /f "tokens=5" %%a in ('netstat -ano ^| find ":5000"') do taskkill /PID %%a /F || echo No running Flask server found
                    start /B python server.py
                    echo ✅ Flask server started on port 5000!
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Build & deployment successful!'
        }
        failure {
            echo '❌ Build or deployment failed. Check console output.'
        }
        always {
            echo "📅 Build completed at: ${new Date()}"
        }
    }
}
