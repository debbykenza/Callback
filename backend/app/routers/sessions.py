from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import InterviewSession, User
from app.schemas import AnswerIn, SessionCreateIn, SessionOut, SummaryOut
from app.services.interview_service import clone_session, create_session, submit_answer
from app.services.summary_service import generate_summary

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _get_owned_session_or_404(db: Session, session_id: str, user_id: str) -> InterviewSession:
    session = db.get(InterviewSession, session_id)
    if session is None or session.user_id != user_id:
        raise HTTPException(404, "Entretien introuvable.")
    return session


@router.post("", response_model=SessionOut)
def create(payload: SessionCreateIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        session = create_session(db, payload.cv_id, payload.job_offer_id, payload.persona, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return session


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_owned_session_or_404(db, session_id, current_user.id)


@router.post("/{session_id}/messages", response_model=SessionOut)
def answer(
    session_id: str,
    payload: AnswerIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = _get_owned_session_or_404(db, session_id, current_user.id)
    try:
        session = submit_answer(db, session, payload.content)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return session


@router.post("/{session_id}/end", response_model=SummaryOut)
def end(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = _get_owned_session_or_404(db, session_id, current_user.id)
    summary = generate_summary(db, session)
    return summary


@router.get("/{session_id}/summary", response_model=SummaryOut)
def get_summary(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = _get_owned_session_or_404(db, session_id, current_user.id)
    if session.summary is None:
        raise HTTPException(404, "Pas encore de fiche recapitulative pour cet entretien.")
    return session.summary


@router.post("/{session_id}/retry", response_model=SessionOut)
def retry(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = _get_owned_session_or_404(db, session_id, current_user.id)
    new_session = clone_session(db, session)
    return new_session
