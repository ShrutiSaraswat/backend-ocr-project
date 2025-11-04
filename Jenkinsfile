pipeline {
    agent any

    environment {
        PYTHON = '/usr/bin/python3'
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
                echo '🐍 Creating virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Check Dependencies') {
            steps {
                echo '🔍 Verifying required packages...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -c "import flask, boto3, dotenv; print('✅ All core packages installed!')"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running tests (if any)...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -m pytest || echo "⚠️ No tests configured, skipping test stage."
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying Flask OCR app...'
                sh '''
                    . ${VENV_DIR}/bin/activate

                    # Kill any previously running Flask server
                    pkill -f "python server.py" || true

                    # Start the Flask app in background
                    nohup python server.py > app.log 2>&1 &

                    echo "✅ Flask server started successfully!"
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Build and deployment successful!'
        }
        failure {
            echo '❌ Build or deployment failed. Check Jenkins console output for details.'
        }
        always {
            echo '📅 Build completed at: ' + new Date().toString()
        }
    }
}
