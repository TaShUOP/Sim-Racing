pipeline {
    agent {
        label 'Main'
    }

    environment {
        IMAGE_NAME = "f1-telemetry"
        CONTAINER_NAME = "f1-telemetry"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "whoami"
                sh """
                    docker build \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        -t ${IMAGE_NAME}:latest \
                        .
                """
            }
        }

        stage('Stop Existing Container') {
            steps {
                sh """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                """
            }
        }

        stage('Deploy Container') {
            steps {
                sh """
                    docker run -d \
                        --restart unless-stopped \
                        --name ${CONTAINER_NAME} \
                        -p 1223:1223 \
                        -p 1224:1224 \
                        -p 20777:20777/udp \
                        ${IMAGE_NAME}:latest
                """
            }
        }
    }

    post {
        success {
            echo "Deployment Successful!"
            sh "docker ps"
        }

        failure {
            echo "Deployment Failed!"
        }
    }
}
