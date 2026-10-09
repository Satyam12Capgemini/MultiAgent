from app.core.config import settings
from app.llm.client import LLMClient
from app.llm.fake import FakeLLMClient
from app.llm.generative_engine import GenerativeEngineClient

_cached_client = None

def get_llm_client() -> LLMClient:
    global _cached_client
    if _cached_client is not None:
        return _cached_client

    if settings.LLM_MODE == "engine" and settings.GENAI_API_KEY != "mock-key":
        _cached_client = GenerativeEngineClient()
    else:
        _cached_client = FakeLLMClient()

    return _cached_client
