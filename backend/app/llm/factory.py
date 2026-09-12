from functools import lru_cache

from app.config import get_settings
from app.llm.base import EmbeddingProvider, LLMProvider
from app.llm.gemini_provider import GeminiEmbeddingProvider, GeminiLLMProvider
from app.llm.mock_provider import MockEmbeddingProvider, MockLLMProvider
from app.llm.ollama_provider import OllamaEmbeddingProvider, OllamaLLMProvider
from app.llm.openai_provider import OpenAIEmbeddingProvider, OpenAILLMProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "ollama":
        return OllamaLLMProvider(settings.ollama_base_url, settings.ollama_model)
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("LLM_PROVIDER=openai mais OPENAI_API_KEY est vide (voir .env)")
        return OpenAILLMProvider(settings.openai_api_key, settings.openai_model)
    if settings.llm_provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("LLM_PROVIDER=gemini mais GEMINI_API_KEY est vide (voir .env)")
        return GeminiLLMProvider(settings.gemini_api_key, settings.gemini_text_model)
    return MockLLMProvider()


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.llm_provider == "ollama":
        return OllamaEmbeddingProvider(settings.ollama_base_url, settings.ollama_embed_model)
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("LLM_PROVIDER=openai mais OPENAI_API_KEY est vide (voir .env)")
        return OpenAIEmbeddingProvider(settings.openai_api_key, settings.openai_embed_model)
    if settings.llm_provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("LLM_PROVIDER=gemini mais GEMINI_API_KEY est vide (voir .env)")
        return GeminiEmbeddingProvider(settings.gemini_api_key, settings.gemini_embed_model)
    return MockEmbeddingProvider()
