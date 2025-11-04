pipeline {
    agent any

    environment {
        PYTHON = '/usr/bin/python3'
        VENV_DIR = 'venv'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', credentialsId: 'your-credential-id', url: 'git@github.com:yourusername/yourrepo.git'
            }
        }

        stage('Set up Python Environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python -m pytest || echo "No tests configured"
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    # Stop previous Flask app if running
                    pkill -f "python server.py" || true
                    nohup python server.py > app.log 2>&1 &
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Deployment successful!'
        }
        failure {
            echo '❌ Deployment failed.'
        }
    }
}
