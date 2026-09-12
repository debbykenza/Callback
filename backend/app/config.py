from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'application, lue depuis les variables d'environnement / .env.

    Voir .env.example pour la liste complete et des commentaires sur chaque valeur.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://callback:callback@localhost:5432/callback"

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 jours

    llm_provider: str = "mock"  # mock | ollama | openai | gemini

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    ollama_embed_model: str = "nomic-embed-text"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embed_model: str = "text-embedding-3-small"

    gemini_api_key: str = ""
    gemini_live_model: str = "gemini-3.1-flash-live-preview"
    gemini_text_model: str = "gemini-flash-latest"
    gemini_embed_model: str = "gemini-embedding-001"
    gemini_voice_map_claire: str = "Aoede"
    gemini_voice_map_marc: str = "Charon"
    gemini_voice_map_lea: str = "Kore"
    gemini_voice_map_hugo: str = "Puck"

    frontend_origin: str = "http://localhost:5173"

    def gemini_voice_for(self, persona: str) -> str:
        return {
            "claire": self.gemini_voice_map_claire,
            "marc": self.gemini_voice_map_marc,
            "lea": self.gemini_voice_map_lea,
            "hugo": self.gemini_voice_map_hugo,
        }.get(persona, "Aoede")


@lru_cache
def get_settings() -> Settings:
    return Settings()
