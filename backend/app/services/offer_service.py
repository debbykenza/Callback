from sqlalchemy.orm import Session

from app.llm.factory import get_llm_provider
from app.models import JobOffer


def ingest_offer(db: Session, raw_text: str, user_id: str) -> JobOffer:
    if not raw_text.strip():
        raise ValueError("Le texte de l'offre est vide.")

    llm = get_llm_provider()
    structured = llm.extract_offer_structured(raw_text)

    offer = JobOffer(
        user_id=user_id,
        raw_text=raw_text,
        title=structured.get("title", "Poste"),
        company=structured.get("company", "Entreprise"),
        seniority=structured.get("seniority", "Non precise"),
        required_skills=structured.get("required_skills", []),
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer
