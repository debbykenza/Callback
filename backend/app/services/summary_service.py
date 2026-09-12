from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.llm.factory import get_llm_provider
from app.models import InterviewSession, InterviewSummary, JobOffer


def generate_summary(db: Session, session: InterviewSession) -> InterviewSummary:
    if session.summary is not None:
        return session.summary

    job_offer = db.get(JobOffer, session.job_offer_id)
    transcript = [
        {"role": m.role, "content": m.content, "is_followup": m.is_followup} for m in session.messages
    ]

    llm = get_llm_provider()
    result = llm.generate_summary(transcript, job_offer.title, job_offer.required_skills)

    summary = InterviewSummary(
        session_id=session.id,
        overall_comment=result["overall_comment"],
        strengths=result["strengths"],
        improvements=result["improvements"],
        criteria=result["criteria"],
        score=result.get("score") or (
            round(sum(c["value"] for c in result["criteria"]) / len(result["criteria"])) if result["criteria"] else 0
        ),
    )
    db.add(summary)
    session.status = "ended"
    session.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(summary)
    return summary
