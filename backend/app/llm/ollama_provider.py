"""Fournisseur LLM utilisant un modele local via Ollama (gratuit, aucune cle API).

Necessite qu'Ollama tourne en local (`ollama serve`) avec les modeles
OLLAMA_MODEL et OLLAMA_EMBED_MODEL deja telecharges (`ollama pull llama3.1`,
`ollama pull nomic-embed-text`).
"""

import httpx

from app.llm.base import CVStructured, EmbeddingProvider, LLMProvider, OfferStructured, SummaryResult
from app.llm.json_utils import parse_json_response


class OllamaLLMProvider(LLMProvider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _chat(self, system: str, user: str) -> str:
        resp = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def _chat_json(self, system: str, user: str) -> dict:
        text = self._chat(system + "\nReponds UNIQUEMENT avec un objet JSON valide, sans texte autour.", user)
        return parse_json_response(text)

    def extract_cv_structured(self, raw_text: str) -> CVStructured:
        data = self._chat_json(
            "Tu extrais les informations cles d'un CV. Renvoie un JSON avec les cles "
            '"skills" (liste de competences techniques) et "experiences" (liste de '
            "phrases courtes decrivant les projets/experiences marquants).",
            raw_text[:6000],
        )
        return {"skills": data.get("skills", []), "experiences": data.get("experiences", [])}

    def extract_offer_structured(self, raw_text: str) -> OfferStructured:
        data = self._chat_json(
            "Tu extrais les informations cles d'une offre d'emploi. Renvoie un JSON avec "
            'les cles "title", "company", "seniority" et "required_skills" (liste).',
            raw_text[:6000],
        )
        return {
            "title": data.get("title", "Poste"),
            "company": data.get("company", "Entreprise"),
            "seniority": data.get("seniority", "Non precise"),
            "required_skills": data.get("required_skills", []),
        }

    def generate_question(
        self,
        persona_name: str,
        persona_tag: str,
        skill: str,
        cv_context: str,
        job_title: str,
        is_opening: bool,
        is_closing: bool,
    ) -> str:
        system = (
            f"Tu es {persona_name}, une recruteuse/recruteur virtuel de style '{persona_tag}' qui mene "
            f"un entretien d'embauche pour le poste de {job_title}. Pose UNE seule question, "
            "naturelle et concise, sans preambule."
        )
        if is_opening:
            user = "Pose la question d'ouverture d'entretien (presentation du candidat)."
        elif is_closing:
            user = "Pose la question de cloture d'entretien (motivation pour le poste)."
        else:
            user = (
                f"Pose une question qui evalue la competence '{skill}', en t'appuyant si pertinent "
                f"sur cet extrait du CV du candidat : {cv_context[:400]}"
            )
        return self._chat(system, user).strip()

    def assess_specificity(self, answer: str) -> bool:
        data = self._chat_json(
            "Tu evalues si une reponse d'entretien est assez concrete (exemple precis, contexte, "
            'resultat) ou trop vague/generique. Renvoie {"specific": true} ou {"specific": false}.',
            answer,
        )
        return bool(data.get("specific", True))

    def generate_followup(self, persona_name: str, skill: str, previous_question: str) -> str:
        system = f"Tu es {persona_name}, en entretien d'embauche. La reponse precedente etait trop vague."
        user = (
            f"Relance le candidat pour obtenir un exemple concret lie a '{skill}', "
            "en une phrase naturelle."
        )
        return self._chat(system, user).strip()

    def generate_summary(self, transcript: list[dict], job_title: str, required_skills: list[str]) -> SummaryResult:
        transcript_text = "\n".join(f"{m['role']}: {m['content']}" for m in transcript)
        data = self._chat_json(
            "Tu es coach d'entretien. A partir du transcript fourni, renvoie un JSON avec les cles "
            '"overall_comment" (2-3 phrases), "strengths" (liste de 2-3 points forts precis), '
            '"improvements" (liste de 2-3 points a travailler precis), "criteria" (liste de 3 objets '
            '{"label", "value"} avec value entre 0 et 100) et "score" (entier 0-100, moyenne ponderee).',
            f"Poste : {job_title}\nCompetences attendues : {', '.join(required_skills)}\n\nTranscript :\n{transcript_text}",
        )
        return {
            "overall_comment": data.get("overall_comment", ""),
            "strengths": data.get("strengths", []),
            "improvements": data.get("improvements", []),
            "criteria": data.get("criteria", []),
            "score": int(data.get("score", 0)),
        }


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def embed(self, text: str) -> list[float]:
        resp = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]
