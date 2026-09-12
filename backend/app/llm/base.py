from abc import ABC, abstractmethod
from typing import TypedDict


class CVStructured(TypedDict):
    skills: list[str]
    experiences: list[str]


class OfferStructured(TypedDict):
    title: str
    company: str
    seniority: str
    required_skills: list[str]


class SummaryResult(TypedDict):
    overall_comment: str
    strengths: list[str]
    improvements: list[str]
    criteria: list[dict]


class LLMProvider(ABC):
    """Interface commune a tous les fournisseurs de langage (mock, Ollama, OpenAI...).

    Chaque implementation encapsule sa propre facon d'appeler le modele ; le reste de
    l'application ne connait jamais le fournisseur concret (voir app/llm/factory.py).
    """

    @abstractmethod
    def extract_cv_structured(self, raw_text: str) -> CVStructured:
        """Extrait competences et experiences-cles d'un CV brut (texte issu du PDF)."""

    @abstractmethod
    def extract_offer_structured(self, raw_text: str) -> OfferStructured:
        """Extrait poste / entreprise / seniorite / competences requises d'une offre."""

    @abstractmethod
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
        """Genere la question d'entretien pour un 'slot' donne, en s'appuyant sur un
        extrait pertinent du CV (retrieval) pour que la question reference du concret."""

    @abstractmethod
    def assess_specificity(self, answer: str) -> bool:
        """Renvoie True si la reponse du candidat est deja assez concrete/precise,
        False si une relance ('donne un exemple concret') est utile."""

    @abstractmethod
    def generate_followup(self, persona_name: str, skill: str, previous_question: str) -> str:
        """Genere une relance quand la reponse precedente etait trop vague."""

    @abstractmethod
    def generate_summary(
        self,
        transcript: list[dict],
        job_title: str,
        required_skills: list[str],
    ) -> SummaryResult:
        """Genere la fiche recapitulative (points forts / a travailler / criteres notes)."""


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Renvoie le vecteur d'embedding d'un texte."""
