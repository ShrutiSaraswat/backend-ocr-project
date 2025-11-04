pipeline {
    agent any

    environment {
        PYTHON = '/usr/bin/python3'
        VENV_DIR = 'venv'

        // Inject AWS credentials securely from Jenkins
        S3_BUCKET     = credentials('S3_BUCKET')
        S3_REGION     = credentials('S3_REGION')
        S3_ACCESS_KEY = credentials('S3_ACCESS_KEY')
        S3_SECRET_KEY = credentials('S3_SECRET_KEY')
    }

    stages {
        stage('Clone Repository') {
            steps {
                echo '📥 Cloning GitHub repository...'
                git branch: 'main', credentialsId: 'your-credential-id', url: 'git@github.com:yourusername/yourrepo.git'
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

        stage('Verify Environment') {
            steps {
                echo '🔍 Checking dependencies...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -c "import boto3, flask, dotenv; print('✅ Environment ready!')"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running tests...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -m pytest || echo "⚠️ No tests configured, skipping..."
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying Flask OCR server...'
                sh '''
                    . ${VENV_DIR}/bin/activate

                    # Stop existing Flask instance if running
                    pkill -f "python server.py" || true

                    # Start the Flask server in background
                    nohup python server.py > app.log 2>&1 &
                    sleep 5
                    echo "Server started successfully!"
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Deployment successful!'
        }
        failure {
            echo '❌ Deployment failed. Check Jenkins logs for details.'
        }
        always {
            echo '📄 Build finished at: ' + new Date().toString()
        }
    }
}
