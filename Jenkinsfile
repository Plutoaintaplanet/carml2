pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "your-dockerhub-username/carml-app"
        IMAGE_TAG = "latest"
        VERCEL_SCOPE = "plutoaintaplanet"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                bat 'python -m pip install --upgrade pip setuptools wheel'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install -r requirements.txt'
            }
        }

        stage('Code Quality') {
            steps {
                bat '''
                    python -m pip install flake8
                    flake8 --max-line-length=120 CARML
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([
                    string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')
                ]) {
                    bat '''
                        docker run --rm ^
                        -v "%CD%:/usr/src" ^
                        -w /usr/src ^
                        sonarsource/sonar-scanner-cli:latest ^
                        -Dsonar.projectKey=Plutoaintaplanet_carml2 ^
                        -Dsonar.organization=plutoaintaplanet ^
                        -Dsonar.host.url=https://sonarcloud.io ^
                        -Dsonar.login=%SONAR_TOKEN% ^
                        -Dsonar.sources=CARML
                    '''
                }
            }
        }

        stage('Dependency and Vulnerability Scan') {
            steps {
                bat '''
                    docker run --rm ^
                    -v "%CD%:/project" ^
                    -w /project ^
                    aquasec/trivy:latest ^
                    fs --exit-code 0 --severity HIGH,CRITICAL /project/CARML
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %DOCKER_IMAGE%:%IMAGE_TAG% ."
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_PASS'
                    )
                ]) {
                    bat '''
                        echo %DOCKERHUB_PASS% | docker login -u %DOCKERHUB_USER% --password-stdin
                        docker push %DOCKER_IMAGE%:%IMAGE_TAG%
                    '''
                }
            }
        }

        stage('Deploy to Vercel') {
            steps {
                withCredentials([
                    string(credentialsId: 'vercel-token', variable: 'VERCEL_TOKEN')
                ]) {
                    bat '''
                        docker run --rm ^
                        -v "%CD%:/workspace" ^
                        -w /workspace ^
                        node:20-bullseye ^
                        bash -lc "npm install -g vercel@34 && vercel deploy --prod --token %VERCEL_TOKEN% --confirm --scope %VERCEL_SCOPE%"
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }

        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check console output.'
        }
    }
}