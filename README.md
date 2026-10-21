# Containerized Student Management System with Automated CI/CD Deployment

A beginner-friendly Student Management web application built with **Python, Flask, HTML/CSS/JavaScript, Git, Jenkins, Selenium, and Docker**. It runs locally; no cloud account is required.

## Features
- Add, list, search, edit, and delete student records
- REST API with basic field validation
- JSON-file persistence for this educational demo
- Unit tests with Python's built-in `unittest`
- Optional Selenium browser smoke test
- Docker image and Docker Compose setup
- Jenkins pipeline for checkout, dependency installation, unit tests, and Docker image build

## Requirements
- Windows 11
- Python 3.10 or newer (Python 3.12 recommended)
- Git
- VS Code
- Docker Desktop (for container steps)
- Jenkins (for CI/CD steps)
- Google Chrome (for the Selenium test)

## 1. Run locally
Open this folder in VS Code. In VS Code choose **Terminal → New Terminal**, then run:

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements-dev.txt
py -m flask --app app run --debug
```

Open http://127.0.0.1:5000. Stop the development server with `Ctrl+C`.

If PowerShell blocks virtual-environment activation, use Command Prompt terminal and run:
```bat
.venv\Scripts\activate.bat
```

## 2. Run unit tests
With the virtual environment activated:

```powershell
py -m unittest discover -s tests -p "test_*.py" -v
```

The tests use a temporary data directory so they do not change the app's normal `students.json`.

## 3. Run Selenium browser test
Install dependencies with `py -m pip install -r requirements-dev.txt`. Start the app in Terminal 1. In Terminal 2, activate the same virtual environment and run:

```powershell
py tests/selenium/students.test.py
```

Selenium Manager may download a compatible ChromeDriver on the first run. Chrome must be installed and network access may be needed. The test adds a sample student to the local demo data.

## 4. Run with Docker
Install and start Docker Desktop. From the project directory:

```powershell
docker --version
docker compose up --build -d
```

Open http://localhost:5000. The Compose volume preserves data when the container is recreated. To stop the app:

```powershell
docker compose down
```

To also delete the saved Docker volume and its student records (irreversible):
```powershell
docker compose down --volumes
```

## 5. Upload to your own GitHub repository
Create a new **empty** repository on GitHub named `containerized-student-management-system`. Do not initialize it with a README if you already have this project README. In the VS Code terminal, from this folder:

```powershell
git init
git add .
git commit -m "Initial Student Management System"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/containerized-student-management-system.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your own GitHub username. Never commit passwords, access tokens, or private credentials.

## 6. Jenkins pipeline
This repository includes a `Jenkinsfile` for a **Windows Jenkins agent**. It runs Python unit tests and builds a Docker image.

1. Install Git, Python, and Docker Desktop on the machine running Jenkins. Make sure Jenkins can run `git`, `python`, and `docker` commands.
2. Open Jenkins, then install the **Pipeline** plugin if it is not already installed.
3. Create **New Item → Pipeline**.
4. Under **Pipeline**, choose **Pipeline script from SCM**.
5. Select **Git**, enter your GitHub repository URL, and set **Script Path** to `Jenkinsfile`.
6. Save, then click **Build Now** and open **Console Output**.

If the repository is public, a Git credential is not required. For a private repository, add a GitHub credential in **Manage Jenkins → Credentials** and select it in the job's SCM configuration. Never put a token directly in the Jenkinsfile.

**Windows note:** Jenkins runs under a Windows service account. Docker Desktop may not be accessible to that account by default. If the Docker build stage fails with a Docker connection/permission error, first confirm `docker version` works in the same account Jenkins uses. Do not assume a successful build from your interactive desktop terminal means the Jenkins service can access Docker.

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/students` | List students |
| POST | `/api/students` | Add a student |
| PUT | `/api/students/<id>` | Update a student |
| DELETE | `/api/students/<id>` | Delete a student |

Example POST body:
```json
{
  "name": "Aanya Sharma",
  "email": "aanya@example.com",
  "course": "Computer Science",
  "year": "2nd Year"
}
```

## Project structure
```text
containerized-student-management-system/
├── app.py
├── students.json
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── style.css
└── tests/
    ├── test_app.py
    └── selenium/
        └── students.test.py
```

## Educational-project limitations
This is a local demonstration, not a production student-record system. It uses a JSON file rather than a production database and does not include authentication, role-based access, or production security hardening. Use fictional student details in demos.
