from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import JobOfferIn, JobOfferOut
from app.services.offer_service import ingest_offer

router = APIRouter(prefix="/api/offers", tags=["offers"])


@router.post("", response_model=JobOfferOut)
def create_offer(payload: JobOfferIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        offer = ingest_offer(db, payload.raw_text, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return offer
