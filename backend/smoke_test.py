"""Test de fumee : verifie que le flow complet (inscription -> CV -> offre -> entretien
-> relance -> fin -> fiche -> historique -> retry) fonctionne de bout en bout avec le
fournisseur mock et une base SQLite jetable. Pas fait pour tourner en prod,
juste pour valider que le backend ne plante pas avant de livrer le zip.
"""

import os
import uuid
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./smoke_test.db"
os.environ["LLM_PROVIDER"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

# "with" est necessaire pour que les evenements de demarrage FastAPI (create_all) s'executent.
client = TestClient(app).__enter__()

SAMPLE_CV = Path(__file__).resolve().parent.parent / "sample_data" / "cv_exemple.pdf"


def make_fake_cv_pdf() -> bytes:
    return SAMPLE_CV.read_bytes()


def main():
    health = client.get("/api/health").json()
    print("health:", health)
    assert health["status"] == "ok"

    # Inscription + token, utilise pour tous les appels proteges qui suivent.
    email = f"smoke-{uuid.uuid4().hex[:8]}@test.com"
    register_resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": "motdepasse123", "name": "Smoke Test"},
    )
    assert register_resp.status_code == 201, register_resp.text
    token = register_resp.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("Auth OK, user:", register_resp.json()["user"])

    cv_bytes = make_fake_cv_pdf()
    cv_resp = client.post(
        "/api/cv", files={"file": ("cv.pdf", cv_bytes, "application/pdf")}, headers=auth_headers
    )
    assert cv_resp.status_code == 200, cv_resp.text
    cv = cv_resp.json()
    print("CV structured:", cv["structured"])

    offer_text = (
        "Developpeur Fullstack en alternance\n"
        "Niji Nantes\n"
        "Nous recherchons un(e) alternant(e) pour rejoindre notre equipe fullstack. "
        "Stack : React, FastAPI, PostgreSQL. Profil junior bienvenu."
    )
    offer_resp = client.post("/api/offers", json={"raw_text": offer_text}, headers=auth_headers)
    assert offer_resp.status_code == 200, offer_resp.text
    offer = offer_resp.json()
    print("Offer:", offer)

    session_resp = client.post(
        "/api/sessions",
        json={"cv_id": cv["id"], "job_offer_id": offer["id"], "persona": "claire"},
        headers=auth_headers,
    )
    assert session_resp.status_code == 200, session_resp.text
    session = session_resp.json()
    print("First question (ouverture, pas de relance possible):", session["messages"][-1]["content"])

    # Reponse a la question d'ouverture (jamais de relance sur ce slot par design)
    intro_resp = client.post(
        f"/api/sessions/{session['id']}/messages",
        json={"content": "Je suis en premiere annee du cycle ingenieur informatique a l'UTBM, apres un diplome de developpement logiciel."},
        headers=auth_headers,
    )
    assert intro_resp.status_code == 200, intro_resp.text
    session = intro_resp.json()
    print("Question sur une competence:", session["messages"][-1]["content"])

    # Reponse volontairement vague sur un slot de competence -> doit declencher une relance
    vague_resp = client.post(
        f"/api/sessions/{session['id']}/messages", json={"content": "Oui j'ai fait ca."}, headers=auth_headers
    )
    assert vague_resp.status_code == 200, vague_resp.text
    session = vague_resp.json()
    last = session["messages"][-1]
    print("Apres reponse vague -> is_followup:", last["is_followup"], "|", last["content"])
    assert last["is_followup"] is True, "une relance etait attendue"

    # Boucle jusqu'a la fin de l'entretien avec des reponses detaillees
    guard = 0
    while True:
        guard += 1
        assert guard < 15, "boucle d'entretien trop longue, logique cassee ?"
        detailed = (
            "Sur le projet LifeCard, j'ai migre l'adapter Vercel et resolu une incompatibilite SQLite "
            "en environnement serverless, ce qui a stabilise le deploiement pour 3 releases suivantes."
        )
        resp = client.post(f"/api/sessions/{session['id']}/messages", json={"content": detailed}, headers=auth_headers)
        assert resp.status_code == 200, resp.text
        session = resp.json()
        print("status:", session["status"], "| dernier message:", session["messages"][-1]["content"][:80])
        if session["status"] != "active":
            break

    end_resp = client.post(f"/api/sessions/{session['id']}/end", headers=auth_headers)
    assert end_resp.status_code == 200, end_resp.text
    summary = end_resp.json()
    print("Summary:", summary)
    assert summary["criteria"]
    assert 0 <= summary["score"] <= 100

    history_resp = client.get("/api/history", headers=auth_headers)
    assert history_resp.status_code == 200, history_resp.text
    history = history_resp.json()
    print("History:", history)
    assert len(history) == 1
    assert history[0]["score"] == summary["score"]

    retry_resp = client.post(f"/api/sessions/{session['id']}/retry", headers=auth_headers)
    assert retry_resp.status_code == 200, retry_resp.text
    print("Retry session id:", retry_resp.json()["id"])

    # Un autre utilisateur ne doit voir ni la session ni l'historique du premier.
    other_register = client.post(
        "/api/auth/register",
        json={"email": f"smoke-other-{uuid.uuid4().hex[:8]}@test.com", "password": "motdepasse123"},
    )
    other_headers = {"Authorization": f"Bearer {other_register.json()['access_token']}"}
    other_history = client.get("/api/history", headers=other_headers)
    assert other_history.json() == [], "l'historique ne doit pas fuiter entre comptes"
    other_session_access = client.get(f"/api/sessions/{session['id']}", headers=other_headers)
    assert other_session_access.status_code == 404, "un autre compte ne doit pas acceder a cette session"

    print("\nSMOKE TEST OK — le flow complet fonctionne de bout en bout.")


if __name__ == "__main__":
    main()
