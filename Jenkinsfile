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

        stage('OWASP Dependency-Check') {
            options { timeout(time: 60, unit: 'MINUTES') }
            steps {
                withCredentials([string(credentialsId: 'nvd-api-key', variable: 'NVD_KEY')]) {
                    sh '''
                        mkdir -p odc-report /var/jenkins_home/odc-data
                        SITE=$(ls -d services/product-service/venv/lib/python3*/site-packages)
                        /opt/dependency-check/bin/dependency-check.sh \
                          --project ShopKart \
                          --scan "$SITE" \
                          --scan services/product-service/requirements.txt \
                          --enableExperimental \
                          --disableOssIndex \
                          --noupdate \
                          --suppression dependency-check-suppressions.xml \
                          --format HTML --format JSON \
                          --out odc-report \
                          --data /var/jenkins_home/odc-data \
                          --nvdApiKey "$NVD_KEY" \
                          --failOnCVSS 9
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'odc-report/**', allowEmptyArchive: true
                }
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build -t ${IMAGE}:${BUILD_NUMBER} services/product-service'
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker tag ${IMAGE}:${BUILD_NUMBER} $DH_USER/${IMAGE}:${BUILD_NUMBER}
                        docker tag ${IMAGE}:${BUILD_NUMBER} $DH_USER/${IMAGE}:latest
                        docker push $DH_USER/${IMAGE}:${BUILD_NUMBER}
                        docker push $DH_USER/${IMAGE}:latest
                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success { echo 'Pipeline passed' }
        failure { echo 'Pipeline failed' }
    }
}
