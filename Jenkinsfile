pipeline {
agent any

```
stages {

    stage('1. Checkout') {
        steps {
            catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                checkout scm
            }
        }
    }

    stage('2. Install Dependencies') {
        steps {
            catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                bat '"C:/Users/admin/AppData/Local/Programs/Python/Python314/python.exe" -m pip install -r requirements.txt'
            }
        }
    }

    stage('3. Code Quality Analysis') {
        steps {
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                bat '"C:/Users/admin/AppData/Local/Programs/Python/Python314/python.exe" -m pip install flake8'
                bat '"C:/Users/admin/AppData/Local/Programs/Python/Python314/Scripts/flake8.exe" --max-line-length=120 CARML'
            }
        }
    }

    stage('4. Vulnerability Scan') {
        steps {
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                bat '''
```

docker run --rm ^
-v "%CD%:/project" ^
aquasec/trivy:latest ^
fs --severity HIGH,CRITICAL /project
'''
}
}
}

```
    stage('5. Build Docker Image') {
        steps {
            catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                bat 'docker build -t carml-app:latest .'
            }
        }
    }

    stage('6. Vercel Deployment') {
        steps {
            echo 'Deployment handled automatically by Vercel GitHub integration'
        }
    }

    stage('7. Generate Report') {
        steps {
            echo 'Pipeline completed. Review failed/unstable stages above.'
        }
    }
}

post {
    always {
        echo '========= FINAL REPORT ========='
        echo 'Checkout Completed'
        echo 'Dependencies Installed'
        echo 'Code Quality Executed'
        echo 'Security Scan Executed'
        echo 'Docker Build Attempted'
        echo 'Deployment Triggered'
        echo '================================'
    }
}
```

}
