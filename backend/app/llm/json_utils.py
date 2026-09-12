import json
import re


def parse_json_response(text: str) -> dict:
    """Extrait un objet JSON de la reponse d'un LLM, en tolerant les blocs ```json ... ```
    ou du texte autour. Leve ValueError si rien d'exploitable n'est trouve."""

    cleaned = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if brace_match:
            cleaned = brace_match.group(0)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Reponse LLM non-JSON exploitable : {text[:200]}") from exc
