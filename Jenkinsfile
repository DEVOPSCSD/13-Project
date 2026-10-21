// Declarative pipeline for a WINDOWS Jenkins agent (uses bat). Requires Git, Python 3.10+ and
// Docker Desktop to be installed and visible to the account running the Jenkins service.
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(name: 'RUN_SELENIUM', defaultValue: false,
                     description: 'Run Selenium tests (needs Chrome + Docker on the agent)')
    }

    environment {
        IMAGE_NAME = 'student-management-system'
        VENV_PY    = "${WORKSPACE}\\.venv\\Scripts\\python.exe"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Check Python') {
            steps { bat 'python --version' }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    if not exist .venv python -m venv .venv
                    "%VENV_PY%" -m pip install --upgrade pip
                    "%VENV_PY%" -m pip install -r backend\\requirements-dev.txt
                '''
            }
        }

        stage('Backend Unit Tests') {
            steps {
                dir('backend') {
                    bat '"%VENV_PY%" -m pytest -v'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker version'
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest .'
            }
        }

        stage('Selenium Tests') {
            when { expression { return params.RUN_SELENIUM } }
            environment {
                APP_PORT = '5001'              // avoids clashing with a manually started app on 5000
                BASE_URL = 'http://localhost:5001'
                COMPOSE_PROJECT_NAME = 'sms_ci'
                SEED_DEMO_DATA = 'false'
            }
            steps {
                bat '"%VENV_PY%" -m pip install -r selenium-tests\\requirements.txt'
                bat 'docker compose up -d --build'
                bat 'powershell -NoProfile -Command "for($i=0;$i -lt 30;$i++){try{Invoke-RestMethod http://localhost:5001/api/health | Out-Null;exit 0}catch{Start-Sleep 2}};exit 1"'
                dir('selenium-tests') {
                    bat '"%VENV_PY%" -m pytest -v'
                }
            }
            post {
                always { bat 'docker compose down -v' }
            }
        }
    }

    post {
        success { echo 'Pipeline finished successfully.' }
        failure { echo 'Pipeline failed - open Console Output and find the first red stage.' }
    }
}
