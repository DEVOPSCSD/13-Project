
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(
            name: 'RUN_SELENIUM',
            defaultValue: false,
            description: 'Run Selenium browser tests after building the Docker image'
        )
    }

    environment {
        IMAGE_NAME = 'student-management-system'

        PYTHON_EXE = 'C:\\Users\\moula\\AppData\\Local\\Programs\\Python\\Python315\\python.exe'
        VENV_PY = "${WORKSPACE}\\.venv\\Scripts\\python.exe"

        DOCKER_EXE = 'C:\\Users\\moula\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'

        APP_PORT = '5001'
        BASE_URL = 'http://localhost:5001'
        COMPOSE_PROJECT_NAME = 'sms_ci'
        SEED_DEMO_DATA = 'false'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat '''
                    if not exist "%PYTHON_EXE%" (
                        echo Python executable not found: %PYTHON_EXE%
                        exit /b 1
                    )
                    "%PYTHON_EXE%" --version
                '''
            }
        }

        stage('Check Docker') {
            steps {
                bat '''
                    if not exist "%DOCKER_EXE%" (
                        echo Docker executable not found: %DOCKER_EXE%
                        exit /b 1
                    )
                    "%DOCKER_EXE%" version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    if not exist ".venv\\Scripts\\python.exe" (
                        "%PYTHON_EXE%" -m venv .venv
                        if errorlevel 1 exit /b 1
                    )

                    "%VENV_PY%" -m pip install --upgrade pip
                    if errorlevel 1 exit /b 1

                    if not exist "backend\\requirements-dev.txt" (
                        echo Missing backend\\requirements-dev.txt
                        exit /b 1
                    )

                    "%VENV_PY%" -m pip install -r backend\\requirements-dev.txt
                    if errorlevel 1 exit /b 1
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
                bat '''
                    "%DOCKER_EXE%" build -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest .
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Selenium Tests') {
            when {
                expression { return params.RUN_SELENIUM }
            }

            steps {
                bat '''
                    if not exist "selenium-tests\\requirements.txt" (
                        echo Missing selenium-tests\\requirements.txt
                        exit /b 1
                    )

                    if not exist "selenium-tests\\test_student_management.py" (
                        echo Missing selenium-tests\\test_student_management.py
                        exit /b 1
                    )

                    "%VENV_PY%" -m pip install -r selenium-tests\\requirements.txt
                    if errorlevel 1 exit /b 1

                    "%DOCKER_EXE%" compose up -d --build
                    if errorlevel 1 exit /b 1

                    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ready=$false; for($i=0;$i -lt 30;$i++){try{$null=Invoke-RestMethod 'http://localhost:5001/api/health'; $ready=$true; break}catch{Start-Sleep -Seconds 2}}; if(-not $ready){Write-Error 'Application health check failed'; exit 1}"
                    if errorlevel 1 exit /b 1
                '''

                dir('selenium-tests') {
                    bat '"%VENV_PY%" -m pytest -v'
                }
            }

            post {
                always {
                    bat(
                        returnStatus: true,
                        script: '"%DOCKER_EXE%" compose down -v'
                    )
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check Console Output for the first failed stage.'
        }
    }
}

