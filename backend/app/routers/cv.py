from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import CVOut
from app.services.cv_service import ingest_cv

router = APIRouter(prefix="/api/cv", tags=["cv"])


@router.post("", response_model=CVOut)
async def upload_cv(file: UploadFile, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(400, "Seuls les fichiers PDF sont acceptes.")
    file_bytes = await file.read()
    try:
        cv = ingest_cv(db, file.filename or "cv.pdf", file_bytes, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return cv
