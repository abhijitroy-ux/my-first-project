from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message_id: Mapped[str] = mapped_column(String, index=True)
    thread_id: Mapped[str] = mapped_column(String, index=True)
    subject: Mapped[str] = mapped_column(String)
    sender: Mapped[str] = mapped_column(String)
    snippet: Mapped[str] = mapped_column(String)
    due_date: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="todo")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TaskCreateRequest(BaseModel):
    email_id: str
    due_date: str | None = None


class TaskResponse(BaseModel):
    id: int
    message_id: str
    thread_id: str
    subject: str
    sender: str
    snippet: str
    due_date: str | None
    status: str

    class Config:
        from_attributes = True
