from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.models import PERSONAS
from app.routers import auth, cv, history, offers, sessions, voice

settings = get_settings()

app = FastAPI(title="Callback API", description="Coach d'entretien IA — backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Pour un vrai projet en production on utiliserait Alembic pour les migrations ;
    # create_all suffit largement pour ce projet local / portfolio.
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health():
    return {"status": "ok", "llm_provider": settings.llm_provider}


@app.get("/api/personas")
def list_personas():
    return [{"id": pid, **meta} for pid, meta in PERSONAS.items()]


app.include_router(auth.router)
app.include_router(cv.router)
app.include_router(offers.router)
app.include_router(sessions.router)
app.include_router(history.router)
app.include_router(voice.router)
