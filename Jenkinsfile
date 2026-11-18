pipeline {
    agent any

    environment {
        IMAGE = 'shopkart'
    }

    stages {
        stage('Test') {
            steps {
                dir('services/product-service') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        python -m pytest -v
                    '''
                }
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t ${IMAGE}:${BUILD_NUMBER} services/product-service'
            }
        }
    }

    post {
        success { echo 'Pipeline passed' }
        failure { echo 'Pipeline failed' }
    }
}
