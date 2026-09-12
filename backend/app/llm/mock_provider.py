"""Fournisseur LLM 'mock' : aucune dependance externe, aucune cle API.

Il simule des reponses structurellement realistes avec de simples heuristiques,
pour que tout le projet tourne immediatement en local. Remplace-le par
OllamaProvider ou OpenAIProvider (voir factory.py) des que tu veux de vraies
reponses generees par un modele.
"""

import hashlib
import re

from app.llm.base import CVStructured, EmbeddingProvider, LLMProvider, OfferStructured, SummaryResult

KNOWN_SKILLS = [
    "React", "Remix", "Vue", "Svelte", "SvelteKit", "TypeScript", "JavaScript",
    "Python", "FastAPI", "Django", "Flask", "PHP", "Laravel", "Java", "Spring Boot",
    "C#", ".NET", "PostgreSQL", "MySQL", "SQL", "Docker", "Kubernetes", "AWS",
    "GCP", "Azure", "Git", "CI/CD", "GraphQL", "REST", "Node.js", "MongoDB",
    "Redis", "Figma", "Machine Learning", "IA", "LLM", "Ollama", "n8n", "Linux",
    "HTML", "CSS", "Tailwind",
]


def _find_skills(text: str) -> list[str]:
    found = []
    lowered = text.lower()
    for skill in KNOWN_SKILLS:
        if skill.lower() in lowered:
            found.append(skill)
    return found or ["fullstack web"]


class MockLLMProvider(LLMProvider):
    def extract_cv_structured(self, raw_text: str) -> CVStructured:
        skills = _find_skills(raw_text)
        lines = [ln.strip() for ln in re.split(r"[\n\.]", raw_text) if len(ln.strip()) > 40]
        experiences = lines[:6] or [raw_text[:200]]
        return {"skills": skills, "experiences": experiences}

    def extract_offer_structured(self, raw_text: str) -> OfferStructured:
        lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
        title = lines[0] if lines else "Poste non precise"
        company = lines[1] if len(lines) > 1 else "Entreprise non precisee"
        lowered = raw_text.lower()
        if "stage" in lowered:
            seniority = "Stage"
        elif "alternance" in lowered:
            seniority = "Alternance"
        elif "junior" in lowered:
            seniority = "Junior"
        elif "senior" in lowered:
            seniority = "Senior"
        else:
            seniority = "Non precise"
        return {
            "title": title[:120],
            "company": company[:120],
            "seniority": seniority,
            "required_skills": _find_skills(raw_text)[:6],
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
        if is_opening:
            return (
                f"Bonjour, merci de prendre le temps. Je suis {persona_name}. "
                "Peux-tu commencer par te presenter et me parler rapidement de ton parcours ?"
            )
        if is_closing:
            return f"Pour finir, qu'est-ce qui t'attire particulierement dans le poste de {job_title} ?"

        if cv_context:
            return (
                f"Tu mentionnes une experience en lien avec {skill}. Peux-tu revenir en detail "
                f"sur ce que tu as fait concretement, en t'appuyant par exemple sur « {cv_context[:140]}... » ?"
            )
        return f"Peux-tu me parler d'une experience concrete ou tu as utilise {skill} ?"

    def assess_specificity(self, answer: str) -> bool:
        words = answer.strip().split()
        has_digit = any(ch.isdigit() for ch in answer)
        has_marker = any(m in answer.lower() for m in ["j'ai", "nous avons", "nous avions", "nous avons du", "resultat"])
        return len(words) >= 22 or (has_digit and has_marker)

    def generate_followup(self, persona_name: str, skill: str, previous_question: str) -> str:
        return (
            f"Peux-tu donner un exemple plus concret ? Un cas precis lie a {skill}, "
            "avec si possible un resultat ou un chiffre a l'appui."
        )

    def generate_summary(self, transcript: list[dict], job_title: str, required_skills: list[str]) -> SummaryResult:
        user_answers = [m for m in transcript if m["role"] == "user"]
        followups_asked = sum(1 for m in transcript if m["role"] == "assistant" and m.get("is_followup"))
        avg_len = (sum(len(a["content"].split()) for a in user_answers) / len(user_answers)) if user_answers else 0

        clarity = max(45, min(95, round(60 + avg_len * 1.1 - followups_asked * 4)))
        structure = max(40, min(92, round(70 - followups_asked * 6)))
        followup_handling = max(35, min(90, round(85 - followups_asked * 12)))
        score = round((clarity + structure + followup_handling) / 3)

        skills_mentioned = [s for s in required_skills if any(s.lower() in a["content"].lower() for a in user_answers)]
        strength_skill = skills_mentioned[0] if skills_mentioned else (required_skills[0] if required_skills else "ton domaine")

        strengths = [
            f"Bonne mise en avant de ton experience en {strength_skill}, avec des elements concrets.",
            "Discours globalement clair et bien relie a des projets reels.",
        ]
        improvements = []
        if followups_asked > 0:
            improvements.append("Anticipe l'exemple concret des la premiere reponse, sans attendre la relance.")
        else:
            improvements.append("Continue a structurer tes reponses avec la methode STAR pour aller encore plus vite a l'essentiel.")
        improvements.append(f"Prepare une reponse assumee sur l'ecart eventuel avec les attentes du poste ({job_title}).")

        return {
            "overall_comment": (
                f"Entretien globalement solide pour le poste de {job_title}. "
                f"{'Quelques relances ont ete necessaires pour obtenir des exemples precis.' if followups_asked else 'Tu es alle assez vite au concret.'}"
            ),
            "strengths": strengths,
            "improvements": improvements,
            "criteria": [
                {"label": "Clarte technique", "value": clarity},
                {"label": "Structure des reponses", "value": structure},
                {"label": "Gestion des relances", "value": followup_handling},
            ],
            "score": score,
        }


class MockEmbeddingProvider(EmbeddingProvider):
    """Embedding deterministe (hash -> vecteur) : pas de vraie semantique, mais stable
    et suffisant pour que le pipeline de retrieval tourne sans dependance externe."""

    DIM = 64

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.DIM
        for i, word in enumerate(re.findall(r"\w+", text.lower())):
            h = int(hashlib.sha256(word.encode()).hexdigest(), 16)
            vec[h % self.DIM] += 1.0 + (i % 3) * 0.01
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / norm for v in vec]
