from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import InterviewSession, User
from app.schemas import HistoryItemOut

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[HistoryItemOut])
def list_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == current_user.id)
        .order_by(desc(InterviewSession.started_at))
        .all()
    )
    return [
        HistoryItemOut(
            id=s.id,
            persona=s.persona,
            status=s.status,
            started_at=s.started_at,
            job_title=s.job_offer.title,
            company=s.job_offer.company,
            cv_filename=s.cv.filename,
            score=s.summary.score if s.summary else None,
        )
        for s in sessions
    ]
