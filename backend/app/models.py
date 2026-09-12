import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CV(Base):
    __tablename__ = "cvs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str] = mapped_column(String)
    raw_text: Mapped[str] = mapped_column(Text)
    # Competences / experiences extraites par le LLM, ex: {"skills": [...], "experiences": [...]}
    structured: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    chunks: Mapped[list["CVChunk"]] = relationship(back_populates="cv", cascade="all, delete-orphan")


class CVChunk(Base):
    """Un fragment du CV (une experience, un projet) + son embedding, pour la recherche RAG."""

    __tablename__ = "cv_chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    cv_id: Mapped[str] = mapped_column(ForeignKey("cvs.id"))
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list] = mapped_column(JSON)  # liste de floats

    cv: Mapped["CV"] = relationship(back_populates="chunks")


class JobOffer(Base):
    __tablename__ = "job_offers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    raw_text: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(String, default="")
    company: Mapped[str] = mapped_column(String, default="")
    seniority: Mapped[str] = mapped_column(String, default="")
    # Liste de competences-cles extraites de l'offre, ex: ["React", "FastAPI", "PostgreSQL"]
    required_skills: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


PERSONAS = {
    "claire": {"name": "Claire", "tag": "Bienveillante, structuree"},
    "marc": {"name": "Marc", "tag": "Direct, technique"},
    "lea": {"name": "Lea", "tag": "Style RH, comportemental"},
    "hugo": {"name": "Hugo", "tag": "Startup, decontracte"},
}


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    cv_id: Mapped[str] = mapped_column(ForeignKey("cvs.id"))
    job_offer_id: Mapped[str] = mapped_column(ForeignKey("job_offers.id"))
    persona: Mapped[str] = mapped_column(String)

    status: Mapped[str] = mapped_column(String, default="active")  # active | ready_to_end | ended

    # Sequence des "slots" de question (competence visee pour chaque tour), decidee a la creation
    slots: Mapped[list] = mapped_column(JSON, default=list)
    current_slot_index: Mapped[int] = mapped_column(Integer, default=0)
    awaiting_followup: Mapped[bool] = mapped_column(Boolean, default=False)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    cv: Mapped["CV"] = relationship()
    job_offer: Mapped["JobOffer"] = relationship()
    messages: Mapped[list["Message"]] = relationship(back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    summary: Mapped["InterviewSummary | None"] = relationship(back_populates="session", cascade="all, delete-orphan", uselist=False)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("interview_sessions.id"))
    role: Mapped[str] = mapped_column(String)  # assistant | user
    content: Mapped[str] = mapped_column(Text)
    is_followup: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    session: Mapped["InterviewSession"] = relationship(back_populates="messages")


class InterviewSummary(Base):
    __tablename__ = "interview_summaries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("interview_sessions.id"), unique=True)
    overall_comment: Mapped[str] = mapped_column(Text)
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    improvements: Mapped[list] = mapped_column(JSON, default=list)
    # [{"label": "Clarte technique", "value": 82}, ...]
    criteria: Mapped[list] = mapped_column(JSON, default=list)
    score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    session: Mapped["InterviewSession"] = relationship(back_populates="summary")
