"""Coeur de la logique d'entretien : enchainement des questions par 'slot' de
competence, relances adaptatives quand une reponse est trop vague, et RAG leger
(retrieval d'un extrait pertinent du CV pour ancrer chaque question).
"""

from sqlalchemy.orm import Session

from app.llm.factory import get_embedding_provider, get_llm_provider
from app.models import PERSONAS, CV, CVChunk, InterviewSession, JobOffer, Message
from app.services.similarity import most_similar

OPENING = "__opening__"
CLOSING = "__closing__"
MAX_SKILL_SLOTS = 3


def _build_slots(job_offer: JobOffer) -> list[str]:
    skills = job_offer.required_skills[:MAX_SKILL_SLOTS] or ["ton parcours"]
    return [OPENING, *skills, CLOSING]


def _retrieve_cv_context(db: Session, cv_id: str, skill: str) -> str:
    chunks = db.query(CVChunk).filter(CVChunk.cv_id == cv_id).all()
    if not chunks:
        return ""
    embedder = get_embedding_provider()
    query_vec = embedder.embed(skill)
    candidates = [(c.content, c.embedding) for c in chunks]
    top = most_similar(query_vec, candidates, top_k=1)
    return top[0] if top else ""


def create_session(db: Session, cv_id: str, job_offer_id: str, persona: str, user_id: str) -> InterviewSession:
    if persona not in PERSONAS:
        raise ValueError(f"Persona inconnue : {persona}")

    cv = db.get(CV, cv_id)
    job_offer = db.get(JobOffer, job_offer_id)
    if cv is None or job_offer is None:
        raise ValueError("CV ou offre introuvable.")
    if cv.user_id != user_id or job_offer.user_id != user_id:
        raise ValueError("CV ou offre introuvable.")

    slots = _build_slots(job_offer)
    session = InterviewSession(
        user_id=user_id,
        cv_id=cv_id,
        job_offer_id=job_offer_id,
        persona=persona,
        slots=slots,
        current_slot_index=0,
        status="active",
    )
    db.add(session)
    db.flush()

    llm = get_llm_provider()
    persona_meta = PERSONAS[persona]
    question = llm.generate_question(
        persona_name=persona_meta["name"],
        persona_tag=persona_meta["tag"],
        skill=slots[0],
        cv_context="",
        job_title=job_offer.title,
        is_opening=True,
        is_closing=False,
    )
    db.add(Message(session_id=session.id, role="assistant", content=question, is_followup=False))
    db.commit()
    db.refresh(session)
    return session


def submit_answer(db: Session, session: InterviewSession, content: str) -> InterviewSession:
    if session.status != "active":
        raise ValueError("Cet entretien est deja termine.")

    llm = get_llm_provider()
    persona_meta = PERSONAS[session.persona]
    job_offer = db.get(JobOffer, session.job_offer_id)

    db.add(Message(session_id=session.id, role="user", content=content, is_followup=False))

    current_skill = session.slots[session.current_slot_index]
    needs_check = current_skill not in (OPENING, CLOSING)

    if needs_check and not session.awaiting_followup:
        specific_enough = llm.assess_specificity(content)
        if not specific_enough:
            followup = llm.generate_followup(persona_meta["name"], current_skill, previous_question="")
            session.awaiting_followup = True
            db.add(Message(session_id=session.id, role="assistant", content=followup, is_followup=True))
            db.commit()
            db.refresh(session)
            return session

    # La reponse est jugee assez concrete (ou c'etait deja une relance) : on avance.
    session.awaiting_followup = False
    session.current_slot_index += 1

    if session.current_slot_index >= len(session.slots):
        session.status = "ready_to_end"
        db.add(
            Message(
                session_id=session.id,
                role="assistant",
                content="Merci pour tes reponses, on s'arrete la. Tu peux terminer l'entretien pour voir ta fiche recapitulative.",
                is_followup=False,
            )
        )
        db.commit()
        db.refresh(session)
        return session

    next_skill = session.slots[session.current_slot_index]
    is_closing = next_skill == CLOSING
    cv_context = "" if is_closing else _retrieve_cv_context(db, session.cv_id, next_skill)

    question = llm.generate_question(
        persona_name=persona_meta["name"],
        persona_tag=persona_meta["tag"],
        skill=next_skill,
        cv_context=cv_context,
        job_title=job_offer.title,
        is_opening=False,
        is_closing=is_closing,
    )
    db.add(Message(session_id=session.id, role="assistant", content=question, is_followup=False))
    db.commit()
    db.refresh(session)
    return session


def clone_session(db: Session, session: InterviewSession) -> InterviewSession:
    """Utilise pour 'Retenter l'entretien' : meme CV / offre / persona, nouvelle session vierge."""
    return create_session(db, session.cv_id, session.job_offer_id, session.persona, user_id=session.user_id)
