pipeline {
    environment {
        AWS_REGION = 'ap-south-1'
        ECR_REPO_NAME = 'fastapi-app'
        ECR_REGISTRY = "151738272815.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"
        DOCKER_IMAGE_TAG = "${env.BUILD_NUMBER}" // Unique identifier for immutable tag
        EC2_IP = '13.202.239.186'

        GIT_CREDENTIALS_ID = 'github_creds'
        DOCKER_CREDENTIALS_ID = 'aws_ecr_access_key'
        // DOCKER_SECRET_ID = 'aws_ecr_secret_key'
        SSH_CREDENTIALS_ID = 'ec2_ssh_creds'
    }

    agent any

    stages {
        stage('Clone repository') {
            steps {
                git credentialsId: "${GIT_CREDENTIALS_ID}", url: 'https://github.com/PavanKumar-Kakarla/fastapi_application.git'
            }
        }

        stage('Build and Push Docker Image with Docker-Compose') {
            steps {
                script {
                    //  Login to AWS ECR
                    withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'AWS_ACCESS_KEY', passwordVariable: 'AWS_SECRET_KEY')]) {
                        sh "aws configure set aws_access_key_id ${AWS_ACCESS_KEY}"
                        sh "aws configure set aws_secret_access_key ${AWS_SECRET_KEY}"
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}"
                    }

                    // Build and tag the image using docker-compose
                    sh "docker-compose -f docker-compose.yml build web"
                    sh "docker tag ${ECR_REPO_NAME}:latest ${ECR_REGISTRY}:${DOCKER_IMAGE_TAG}"

                    // Push the image to AWS ECR
                    sh "docker push ${ECR_REGISTRY}:${DOCKER_IMAGE_TAG}"
                    
                }
            }
        }

        stage('Deploy to EC2 with Docker-Compose') {
            steps {
                script {
                    sshagent(["${SSH_CREDENTIALS_ID}"]) {
                        // Send docker-compose.yml to the EC2 instance
                        sh "scp -o StrictHostKeyChecking=no docker-compose.yml ec2-user@${EC2_IP}:/home/ec2-user/docker-compose.yml"

                        // Login to AWS ECR on the EC2 instance using the same credentials
                        withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", usernameVariable: 'AWS_ACCESS_KEY', passwordVariable: 'AWS_SECRET_KEY')]) {
                            sh """
                                ssh -o StrictHostKeyChecking=no ec2-user@${EC2_IP} '
                                aws configure set aws_access_key_id ${AWS_ACCESS_KEY};
                                aws configure set aws_secret_access_key ${AWS_SECRET_KEY};
                                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}'
                            """
                        }

                        // Update docker-compose file with new image tag
                        sh "ssh -o StrictHostKeyChecking=no ec2-user@${EC2_IP} 'sed -i \"s|image: ${ECR_REPO_NAME}:latest|image: ${ECR_REGISTRY}:${DOCKER_IMAGE_TAG}|\" /home/ec2-user/docker-compose.yml'"
                            
                        // Pull the new image, remove old containers, and launch updated services
                        sh "ssh -o StrictHostKeyChecking=no ec2-user@${EC2_IP} 'docker-compose -f /home/ec2-user/docker-compose.yml pull web'"
                        sh "ssh -o StrictHostKeyChecking=no ec2-user@${EC2_IP} 'docker-compose -f /home/ec2-user/docker-compose.yml down || true'"
                        sh "ssh -o StrictHostKeyChecking=no ec2-user@${EC2_IP} 'docker-compose -f /home/ec2-user/docker-compose.yml up -d --force-recreate --remove-orphans'"
                    }
                }
            }
        }
    }
}