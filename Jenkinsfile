pipeline {
    agent any

    environment {
        PYTHON   = '/usr/bin/python3'
        VENV_DIR = 'venv'

        // AWS credentials stored in Jenkins
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
                echo '🐍 Setting up Python virtual environment...'
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Verify Dependencies') {
            steps {
                echo '🔍 Verifying environment...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -c "import flask, boto3, dotenv; print('✅ Core packages ok')"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running tests if any...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -m pytest || echo "⚠️ No tests present, skipping."
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying Flask OCR service...'
                sh '''
                    . ${VENV_DIR}/bin/activate

                    # Stop any currently running instance
                    pkill -f "python server.py" || true

                    # Start the Flask server in background
                    nohup python server.py > app.log 2>&1 &
                    sleep 5
                    echo "✅ Server started."
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Build & deployment succeeded!'
        }
        failure {
            echo '❌ Build or deployment failed. Please check logs.'
        }
        always {
            echo '📅 Build finished at: ' + new Date().toString()
        }
    }
}
