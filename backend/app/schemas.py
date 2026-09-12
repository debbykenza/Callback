from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = ""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class CVOut(BaseModel):
    id: str
    filename: str
    structured: dict

    model_config = {"from_attributes": True}


class JobOfferIn(BaseModel):
    raw_text: str


class JobOfferOut(BaseModel):
    id: str
    title: str
    company: str
    seniority: str
    required_skills: list[str]

    model_config = {"from_attributes": True}


class SessionCreateIn(BaseModel):
    cv_id: str
    job_offer_id: str
    persona: str


class MessageOut(BaseModel):
    role: str
    content: str
    is_followup: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: str
    persona: str
    status: str
    cv_id: str
    job_offer_id: str
    messages: list[MessageOut]

    model_config = {"from_attributes": True}


class AnswerIn(BaseModel):
    content: str


class CriterionOut(BaseModel):
    label: str
    value: int


class SummaryOut(BaseModel):
    overall_comment: str
    strengths: list[str]
    improvements: list[str]
    criteria: list[CriterionOut]
    score: int

    model_config = {"from_attributes": True}


class HistoryItemOut(BaseModel):
    id: str
    persona: str
    status: str
    started_at: datetime
    job_title: str
    company: str
    cv_filename: str
    score: int | None = None
