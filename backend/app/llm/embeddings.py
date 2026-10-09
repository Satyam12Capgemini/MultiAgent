import hashlib
import math
from typing import List, Protocol
import httpx
from app.core.config import settings
from app.core.logging import logger

class EmbeddingProvider(Protocol):
    async def embed(self, texts: List[str]) -> List[List[float]]:
        ...

class FakeEmbeddingProvider:
    """Deterministic hash-based pseudo-embeddings with dimension=384."""
    def __init__(self, dim: int = 384):
        self.dim = dim

    async def embed(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            vec = [0.0] * self.dim
            words = text.lower().split()
            if not words:
                words = ["empty"]
            for word in words:
                h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dim
                sign = 1.0 if ((h >> 8) % 2 == 0) else -1.0
                vec[idx] += sign
            
            # Normalize vector
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            results.append([x / norm for x in vec])
        return results

class EngineEmbeddingProvider:
    """Uses the Generative Engine embedding HTTP endpoint."""
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def embed(self, texts: List[str]) -> List[List[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient(timeout=settings.GENAI_TIMEOUT_SECONDS) as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json={"input": texts, "model": self.model}
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

def get_embedding_provider() -> EmbeddingProvider:
    if settings.EMBEDDING_PROVIDER == "engine" and settings.GENAI_API_KEY != "mock-key":
        return EngineEmbeddingProvider(
            base_url=settings.GENAI_BASE_URL,
            api_key=settings.GENAI_API_KEY,
            model=settings.GENAI_EMBED_MODEL
        )
    return FakeEmbeddingProvider()
