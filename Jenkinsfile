pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

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

        stage('SonarQube Scan') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh 'sonar-scanner -Dsonar.host.url=http://sonarqube:9000 -Dsonar.token=$SONAR_TOKEN -Dsonar.qualitygate.wait=true'
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
