# Gmail → Tasks Starter API

This repository now contains a simple starter backend for your idea:

- Connect to Gmail with OAuth
- Browse recent emails
- Convert an email into a task
- Store tasks in SQLite

It is intentionally minimal so you can evolve it into a full product.

## Tech stack

- FastAPI
- SQLAlchemy + SQLite
- Google Gmail API (`google-api-python-client`)

## Project structure

```text
app/
  db.py        # SQLAlchemy engine/session setup
  main.py      # FastAPI app, Gmail OAuth flow, API routes
  models.py    # SQLAlchemy + Pydantic models
requirements.txt
```

## 1) Create Google OAuth credentials

1. Open Google Cloud Console.
2. Create or choose a project.
3. Enable **Gmail API**.
4. Configure OAuth consent screen.
5. Create OAuth client credentials for a **Web application**.
6. Add this redirect URI:
   - `http://localhost:8000/auth/google/callback`
7. Download the JSON and save it in project root as `client_secret.json`.

## 2) Install and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Server starts on `http://localhost:8000`.

## 3) Authenticate with Gmail

Visit:

- `http://localhost:8000/auth/google/start`

After sign-in, a `token.json` file will be saved locally.

## 4) Example API usage

List recent emails:

```bash
curl "http://localhost:8000/emails?max_results=5"
```

Create a task from an email ID:

```bash
curl -X POST "http://localhost:8000/tasks/from-email" \
  -H "Content-Type: application/json" \
  -d '{"email_id":"<gmail_message_id>","due_date":"2026-03-01"}'
```

List tasks:

```bash
curl "http://localhost:8000/tasks"
```

## Important notes

- This is a starter and currently assumes one local user.
- Tokens are stored in `token.json`; for production, store encrypted per-user credentials.
- You can later add:
  - User accounts
  - Task statuses/labels/priorities
  - Reminder notifications
  - Gmail Add-on frontend


## 5) Transfer this project to GitHub

### Option A: New GitHub repo (first push)

1. Create an empty repository on GitHub (no README/license).
2. In this project folder, run:

```bash
git init
git add .
git commit -m "Initial Gmail Tasks API"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### Option B: Existing local git repo (most likely your case)

If this folder is already a git repo, just connect remote and push:

```bash
git remote add origin https://github.com/<your-username>/<your-repo>.git
# or, if origin already exists:
# git remote set-url origin https://github.com/<your-username>/<your-repo>.git

git push -u origin $(git branch --show-current)
```

### If GitHub asks for authentication

Use either:
- GitHub CLI: `gh auth login`
- Personal Access Token (PAT) when prompted for password over HTTPS
- SSH remote instead of HTTPS (after adding your SSH key to GitHub)

You can verify remote config with:

```bash
git remote -v
```
