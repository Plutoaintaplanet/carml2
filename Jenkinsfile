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
            bat '"C:/Users/admin/AppData/Local/Programs/Python/Python314/python.exe" -m pip install --upgrade pip setuptools wheel'
        }
    }

    stage('Install Dependencies') {
        steps {
            bat '"C:/Users/admin/AppData/Local/Programs/Python/Python314/python.exe" -m pip install -r requirements.txt'
        }
    }

    stage('Code Quality') {
        steps {
            bat '"C:/Users/admin/AppData/Local/Programs/Python/Python314/python.exe" -m pip install flake8'
            bat '"C:/Users/admin/AppData/Local/Programs/Python/Python314/Scripts/flake8.exe" --max-line-length=120 CARML'
        }
    }

    stage('Build Docker Image') {
        steps {
            bat 'docker build -t %DOCKER_IMAGE%:%IMAGE_TAG% .'
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
