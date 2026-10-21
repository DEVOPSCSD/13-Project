# Containerized Student Management System with Automated CI/CD Deployment

## Abstract
A web-based Student Management System built with Flask and SQLite, with a vanilla HTML/CSS/JavaScript
frontend. It is packaged with Docker and verified by a Jenkins pipeline that runs backend unit tests and
builds the Docker image; Selenium tests verify the website in Chrome.

## Problem statement
Student records kept in spreadsheets are error-prone, hard to search and hard to share. Manual build, test and
deployment steps also cause "works on my machine" problems.

## Objectives
- Provide create / read / update / delete / search for student records through a REST API.
- Validate data on both the frontend and the backend.
- Package the application in a Docker container with persistent storage.
- Automate testing and image building with Jenkins.
- Verify the UI automatically with Selenium.

## Architecture
```
Browser (Chrome) --HTTP--> Flask (gunicorn, port 5000)
                              |-- serves frontend/ at "/"
                              |-- REST API at /api/*
                              `-- SQLite file (Docker volume "student_data")
```
CI/CD flow:
```
GitHub push --> Jenkins: Checkout --> Python check --> Install deps --> Unit tests
                              --> Docker build --> (optional) Selenium tests
```

## Technology stack
Python 3, Flask, SQLite, HTML5/CSS3/JavaScript, Git/GitHub, Docker Desktop, Jenkins, Selenium + Chrome, pytest. No Node.js.

## Team responsibilities
| Member 1 (Backend & DevOps) | Member 2 (Frontend) |
|---|---|
| `backend/`, `Dockerfile`, `docker-compose.yml`, `Jenkinsfile`, `selenium-tests/`, Git/GitHub setup, documentation | `frontend/` (index.html, css/style.css, js/app.js) |

Rule: Member 2 only edits `frontend/`; Member 1 edits everything else. The API contract below and the element IDs in
`index.html` (used by Selenium) must not change without both members agreeing.

## Features
Dashboard counts, add / edit / delete students, search by name, email, course or ID, field validation,
duplicate detection, toast notifications, loading and empty states, responsive layout, health-check endpoint,
persistent database, demo data.

## Folder structure
```
backend/            Flask app (app.py, config.py, database.py, models.py, routes.py, tests/)
frontend/           index.html, css/style.css, js/app.js
selenium-tests/     browser tests
Dockerfile  docker-compose.yml  Jenkinsfile  .env.example  .gitignore  .dockerignore
```

## 1. Run locally (Windows PowerShell)
Prerequisites: Python 3.10+ (`python --version`).
```powershell
cd C:\Projects\containerized-student-management-system
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd backend
..\.venv\Scripts\python.exe -m pytest -v          # backend tests
..\.venv\Scripts\python.exe app.py                # start server
```
Open **http://localhost:5000** in Chrome. Stop with `Ctrl+C`.
(No need to "activate" the venv, so PowerShell's script-execution policy is never an issue.)

## 2. Run with Docker
Install and start Docker Desktop first.
```powershell
cd C:\Projects\containerized-student-management-system
docker --version
docker compose up -d --build        # build + start
docker compose ps                   # status (should become "healthy")
docker compose logs -f              # logs (Ctrl+C to leave)
docker compose down                 # stop (data is kept)
docker compose up -d                # start again - students are still there
docker compose down -v              # stop AND delete the database volume
```
Open **http://localhost:5000**. If port 5000 is busy: `$env:APP_PORT=5050; docker compose up -d --build`, then open port 5050.

Verify persistence: add a student in the browser, run `docker compose down`, then `docker compose up -d`; the student is still listed.
Rebuild after code changes: `docker compose up -d --build`.

## 3. Selenium tests
Install Google Chrome. Start the app (locally or Docker), then in a second PowerShell:
```powershell
cd C:\Projects\containerized-student-management-system
.\.venv\Scripts\python.exe -m pip install -r selenium-tests\requirements.txt
cd selenium-tests
..\.venv\Scripts\python.exe -m pytest -v
```
To watch the browser: `$env:HEADLESS="false"` first. To target another port: `$env:BASE_URL="http://localhost:5050"`.
Selenium Manager (built into Selenium 4.6+) downloads a matching ChromeDriver automatically (needs internet on first run).
Tests create uniquely-named students and delete them afterwards, so demo data is untouched.

## API documentation
All responses: `{"success":true,"message":"...","data":...}` or
`{"success":false,"error":{"code":"...","message":"...","details":{"field":"reason"}}}`.

| Method | Endpoint | Success | Errors |
|---|---|---|---|
| GET | `/api/health` | 200 | 503 |
| GET | `/api/students?search=text` | 200 (+`count`, `total`) | |
| GET | `/api/students/<id>` | 200 | 404 |
| POST | `/api/students` | 201 | 400, 409 |
| PUT | `/api/students/<id>` (all fields) | 200 | 400, 404, 409 |
| DELETE | `/api/students/<id>` | 200 | 404 |

Body for POST/PUT:
```json
{"student_id":"CS2024010","full_name":"Meera Nair","email":"meera@example.com",
 "course":"Computer Science","year_of_study":2,"phone":"9876500000"}
```
PowerShell examples:
```powershell
Invoke-RestMethod http://localhost:5000/api/health
(Invoke-RestMethod http://localhost:5000/api/students).data
$b = @{student_id="CS2024010";full_name="Meera Nair";email="meera@example.com";course="Computer Science";year_of_study=2;phone="9876500000"} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/students -ContentType "application/json" -Body $b
Invoke-RestMethod -Method Delete -Uri http://localhost:5000/api/students/6
```

## GitHub workflow
Replace `YOUR-USERNAME` with your real GitHub username.
```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git clone https://github.com/YOUR-USERNAME/containerized-student-management-system.git
```
**First push (Member 1, after extracting the zip into the cloned folder):**
```powershell
cd C:\Projects\containerized-student-management-system
git add .
git commit -m "Initial project: backend, frontend, Docker, Jenkins, Selenium"
git branch -M main
git push -u origin main
```
**Branches (each member works only in their own area):**
```powershell
git checkout -b backend     # Member 1
git checkout -b frontend    # Member 2 (after: git pull origin main)
git add . ; git commit -m "Describe your change" ; git push -u origin <branch-name>
```
Open a Pull Request on GitHub (branch -> `main`), the other member reviews, then **Merge**. Afterwards everyone runs
`git checkout main ; git pull origin main`. Always `git pull origin main` before starting work. Because members edit
different folders, conflicts are rare. If one happens, Git marks `<<<<<<<` / `=======` / `>>>>>>>` in the file: edit it to keep the
right content, delete the markers, then `git add <file>` and `git commit`.

## Jenkins (Windows)
Jenkins needs a supported Java (JDK 17 or 21) - install from https://www.jenkins.io/download/ (Windows installer, which also
installs it as a service) and a JDK from https://adoptium.net. Open http://localhost:8080 and finish the setup wizard.

**Important:** the Jenkins Windows service runs as a different account than your PowerShell, so it may not see Python/Git/Docker.
- Install Python "for all users" so it is on the system PATH, then restart the Jenkins service.
- For Docker: open `services.msc` -> Jenkins -> Properties -> Log On -> run as your own Windows user (enter your password), restart the service. Docker Desktop must be running.

**Create the job:** New Item -> name `student-management-system` -> **Pipeline** -> Pipeline section: *Pipeline script from SCM* ->
SCM *Git* -> Repository URL `https://github.com/YOUR-USERNAME/containerized-student-management-system.git` ->
Branch `*/main` -> Script Path `Jenkinsfile` -> Save.
For a private repo: Manage Jenkins -> Credentials -> add *Username with password* (GitHub username + a Personal Access Token), then choose it in the job. Never put it in the Jenkinsfile.

**Run:** Build Now -> click the build number -> *Console Output*. Find the first red stage / error line. Typical causes: `'python' is not recognized` (PATH of service), `docker ... pipe` error (Docker not running or service account),
`pytest` failures (read assertion).
To run Selenium: Build with Parameters -> tick `RUN_SELENIUM` (needs Chrome and Docker on the Jenkins machine).

**What is automatic:** once configured, each build checks out, tests and builds the image. A build starts automatically only if you add a trigger
(*Poll SCM* with `H/5 * * * *`, which works locally; GitHub webhooks need a public URL, so use polling). **Not automatic:** the pipeline builds the image
but does not deploy it; run `docker compose up -d` yourself.

## Screenshots (add your own)
Create `docs/screenshots/` and add real screenshots, then reference them here with `![Dashboard](docs/screenshots/dashboard.png)`.
Suggested: dashboard, add form, validation errors, search result, edit, delete confirmation, `pytest` output, `docker compose ps`, Docker Desktop, GitHub repo/PRs, Jenkins stage view, Jenkins console "SUCCESS", Selenium results.

## Limitations
SQLite suits small single-server use; no login/authentication; Jenkins pipeline does not deploy automatically; no pagination.

## Future enhancements
User login and roles, pagination, CSV import/export, PostgreSQL, GitHub webhook trigger with a tunnel, auto-deploy stage.

## Conclusion
The project demonstrates a full workflow: a REST backend, a responsive UI, containerization and automated build/test.

## Demo script (about 5 minutes)
1. Show GitHub repo, branches and merged pull requests. 2. `docker compose up -d --build`, open the site. 3. Add, search, edit, delete a student; show a validation error.
4. Stop and start the container to show persistence. 5. Show Jenkins: Build Now, stage view, console output. 6. Run Selenium tests. 7. Explain who did what.

## Viva questions
- **Why Flask?** Lightweight, easy REST APIs in Python.
- **How is SQL injection prevented?** Parameterised queries (`?` placeholders), never string-built SQL values.
- **Why a Docker volume?** Container filesystems are disposable; the volume keeps `students.db`.
- **What does `/api/health` do?** Checks the DB; Docker's HEALTHCHECK and tests use it.
- **What does Jenkins do here?** Checks out code, installs deps, runs unit tests, builds the image, optionally runs Selenium.
- **Why Selenium?** Tests the real UI end to end like a user. Explicit waits avoid flaky sleeps.
- **Why two branches?** Members work independently; pull requests give review before merging to `main`.
- **Your contribution vs teammate's?** Backend, tests, Docker, Jenkins, Git vs. HTML/CSS/JS UI and its validation.
