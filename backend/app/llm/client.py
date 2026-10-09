from typing import Protocol, TypeVar, List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMClient(Protocol):
    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        ticket_id: Optional[str] = None,
        run_id: Optional[str] = None,
        node: Optional[str] = None
    ) -> str:
        """Standard chat completion returning full response string."""
        ...

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        ticket_id: Optional[str] = None,
        run_id: Optional[str] = None,
        node: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Streaming chat completion yielding text tokens."""
        ...

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        schema: type[T],
        *,
        temperature: float = 0.1,
        ticket_id: Optional[str] = None,
        run_id: Optional[str] = None,
        node: Optional[str] = None
    ) -> T:
        """Structured completion validated against a Pydantic schema."""
        ...

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings for a list of text strings."""
        ...
