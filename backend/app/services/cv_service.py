from sqlalchemy.orm import Session

from app.llm.factory import get_embedding_provider, get_llm_provider
from app.models import CV, CVChunk
from app.services.pdf_utils import extract_text_from_pdf


def ingest_cv(db: Session, filename: str, file_bytes: bytes, user_id: str) -> CV:
    raw_text = extract_text_from_pdf(file_bytes)
    if not raw_text.strip():
        raise ValueError("Impossible d'extraire du texte de ce PDF (fichier scanne/image ?).")

    llm = get_llm_provider()
    embedder = get_embedding_provider()

    structured = llm.extract_cv_structured(raw_text)

    cv = CV(user_id=user_id, filename=filename, raw_text=raw_text, structured=structured)
    db.add(cv)
    db.flush()  # obtient cv.id avant de creer les chunks

    experiences = structured.get("experiences") or [raw_text[:500]]
    for exp in experiences:
        if not exp.strip():
            continue
        chunk = CVChunk(cv_id=cv.id, content=exp.strip(), embedding=embedder.embed(exp))
        db.add(chunk)

    db.commit()
    db.refresh(cv)
    return cv
