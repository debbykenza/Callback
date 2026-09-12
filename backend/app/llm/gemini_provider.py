"""Fournisseur LLM utilisant l'API Gemini "standard" (generation de texte, pas la voix).

Contrairement au fournisseur `mock` (heuristiques de mots-cles, voir mock_provider.py,
biaisees vers le developpement web), celui-ci appelle un vrai modele de langage : il
comprend le CV/l'offre quel que soit le domaine (data, marketing, mecanique...) plutot
que de chercher des mots dans une liste fixe.

Reutilise le SDK `google-genai` deja present dans requirements.txt pour le mode vocal
(app/services/voice_service.py), mais via ses methodes de generation de texte "classiques"
(`Models.generate_content` / `Models.embed_content`), pas l'API Live voix-a-voix.
"""

from google import genai
from google.genai import types

from app.llm.base import CVStructured, EmbeddingProvider, LLMProvider, OfferStructured, SummaryResult
from app.llm.json_utils import parse_json_response


class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _generate(self, system: str, user: str, json_mode: bool = False) -> str:
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type="application/json" if json_mode else None,
        )
        resp = self.client.models.generate_content(model=self.model, contents=user, config=config)
        return resp.text or ""

    def _generate_json(self, system: str, user: str) -> dict:
        text = self._generate(system, user, json_mode=True)
        return parse_json_response(text)

    def extract_cv_structured(self, raw_text: str) -> CVStructured:
        data = self._generate_json(
            "Tu extrais les informations cles d'un CV, quel que soit le domaine du "
            "candidat (informatique, data, mecanique, commerce...). Renvoie un JSON avec "
            'les cles "skills" (liste de competences concretes et specifiques au domaine '
            'du candidat, pas de generalites) et "experiences" (liste de phrases courtes '
            "decrivant les projets/experiences marquants).",
            raw_text[:6000],
        )
        return {"skills": data.get("skills", []), "experiences": data.get("experiences", [])}

    def extract_offer_structured(self, raw_text: str) -> OfferStructured:
        data = self._generate_json(
            "Tu extrais les informations cles d'une offre d'emploi, quel que soit le "
            "domaine du poste (informatique, data, mecanique, commerce...). Renvoie un "
            'JSON avec les cles "title", "company", "seniority" et "required_skills" '
            "(liste de competences concretes et specifiques au poste, tirees du texte de "
            "l'offre, pas de generalites ni de competences web par defaut).",
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
        return self._generate(system, user).strip()

    def assess_specificity(self, answer: str) -> bool:
        data = self._generate_json(
            "Tu evalues si une reponse d'entretien est assez concrete (exemple precis, contexte, "
            'resultat) ou trop vague/generique. Renvoie {"specific": true} ou {"specific": false}.',
            answer,
        )
        return bool(data.get("specific", True))

    def generate_followup(self, persona_name: str, skill: str, previous_question: str) -> str:
        system = f"Tu es {persona_name}, en entretien d'embauche. La reponse precedente etait trop vague."
        user = f"Relance le candidat pour obtenir un exemple concret lie a '{skill}', en une phrase naturelle."
        return self._generate(system, user).strip()

    def generate_summary(self, transcript: list[dict], job_title: str, required_skills: list[str]) -> SummaryResult:
        transcript_text = "\n".join(f"{m['role']}: {m['content']}" for m in transcript)
        data = self._generate_json(
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


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def embed(self, text: str) -> list[float]:
        resp = self.client.models.embed_content(model=self.model, contents=text)
        return list(resp.embeddings[0].values)
