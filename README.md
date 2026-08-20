# Project Portfolio Flask App

Small personal projects portfolio built with Flask and SQLite. This repository provides a minimal CRUD UI for projects plus client-side and server-side search, small automated smoke tests, and a CI workflow.

## Quickstart (Windows)

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell
# or
.\.venv\Scripts\activate     # cmd
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Features

- Add, edit, delete projects (name, description, category, status)
- Client-side search (instant filtering, highlighting, debounce)
- Server-side search for larger datasets (supports `?q=` and highlights matches)
- Status badges with color coding
- A `/reset_db` route to drop and recreate the projects table (development use only)

## Files of interest

- `app.py` — Flask application, DB helpers, server-side search and highlighting
- `templates/` — Jinja2 templates (projects, edit_project, base, etc.)
- `static/` — CSS and JS (search.js implements client-side search)
- `tests/` — smoke tests (pytest and a simple script)
- `.github/workflows/ci.yml` — GitHub Actions CI (starts app and runs pytest)

## Testing

Manual smoke test (no extra deps):

```powershell
python tests/smoke_test.py
```

Pytest (recommended, useful for CI):

```powershell
pytest -q
```

Note: the pytest tests assume the app can be started on http://127.0.0.1:5000. The included CI workflow starts the app before running tests.

## Development notes

- The database file `projects.db` is created in the project root when the app runs.
- It's recommended to ignore the DB and other local artifacts — see .gitignore below.

## Security and production

- The app is intentionally minimal and lacks authentication and CSRF protection. Do not expose it to the public without adding security (Flask-WTF CSRF or auth and HTTPS).
- For production, run under a WSGI server (gunicorn, uWSGI) and move the DB to a managed data store if needed.

## .gitignore recommendations

The repository includes a .gitignore (update locally) — recommended entries:

```
__pycache__/
*.pyc
.venv/
projects.db
Flask_app_backup_*/
page.html
```

## Housekeeping

- If `projects.db` is already tracked in your repo, remove it from Git's index and add it to .gitignore:

```bash
git rm --cached projects.db
git add .gitignore
git commit -m "Ignore local DB and runtime artifacts"
```

If you'd like, I can also:
- Add CSRF protection (Flask-WTF) and basic auth for destructive endpoints
- Add an AJAX server-side search to avoid full-page reloads
- Add a Dockerfile and docker-compose for local development

Tell me which of those you'd like next. "}