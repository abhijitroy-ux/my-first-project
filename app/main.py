import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Task, TaskCreateRequest, TaskResponse

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "client_secret.json")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
TOKEN_FILE = Path(os.getenv("GOOGLE_TOKEN_FILE", "token.json"))

app = FastAPI(title="Gmail Tasks Starter API")
Base.metadata.create_all(bind=engine)


def _build_flow() -> Flow:
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )


def _load_credentials() -> Credentials:
    if not TOKEN_FILE.exists():
        raise HTTPException(status_code=401, detail="Not authenticated. Visit /auth/google/start first.")

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json())

    if not creds.valid:
        raise HTTPException(status_code=401, detail="Google auth invalid. Re-authenticate.")

    return creds


def _gmail_service():
    creds = _load_credentials()
    return build("gmail", "v1", credentials=creds)


def _parse_email_headers(payload: dict) -> tuple[str, str]:
    headers = payload.get("headers", [])
    subject = ""
    sender = ""
    for h in headers:
        name = h.get("name", "").lower()
        if name == "subject":
            subject = h.get("value", "")
        elif name == "from":
            sender = h.get("value", "")
    return subject, sender


@app.get("/")
def root():
    return {
        "message": "Gmail Tasks API is running",
        "auth_url": "/auth/google/start",
    }


@app.get("/auth/google/start")
def auth_google_start():
    flow = _build_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(auth_url)


@app.get("/auth/google/callback")
def auth_google_callback(code: str):
    flow = _build_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials
    TOKEN_FILE.write_text(creds.to_json())
    return {"message": "Authenticated with Google", "token_file": str(TOKEN_FILE)}


@app.post("/tasks/from-email", response_model=TaskResponse)
def create_task_from_email(payload: TaskCreateRequest, db: Session = Depends(get_db)):
    service = _gmail_service()

    message = (
        service.users()
        .messages()
        .get(userId="me", id=payload.email_id, format="metadata")
        .execute()
    )

    subject, sender = _parse_email_headers(message.get("payload", {}))
    task = Task(
        message_id=message["id"],
        thread_id=message.get("threadId", ""),
        subject=subject or "(no subject)",
        sender=sender or "(unknown sender)",
        snippet=message.get("snippet", ""),
        due_date=payload.due_date,
        status="todo",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.created_at.desc()).all()


@app.get("/emails")
def list_recent_emails(max_results: int = 10):
    service = _gmail_service()
    response = service.users().messages().list(userId="me", maxResults=max_results).execute()
    message_refs = response.get("messages", [])

    items = []
    for ref in message_refs:
        full = (
            service.users()
            .messages()
            .get(userId="me", id=ref["id"], format="metadata")
            .execute()
        )
        subject, sender = _parse_email_headers(full.get("payload", {}))
        items.append(
            {
                "id": full["id"],
                "thread_id": full.get("threadId"),
                "subject": subject,
                "sender": sender,
                "snippet": full.get("snippet"),
            }
        )

    return {"emails": items}
