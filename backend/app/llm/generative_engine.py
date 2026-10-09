import json
import time
import asyncio
from typing import List, Dict, Any, Optional, TypeVar, AsyncIterator
import httpx
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.logging import logger
from app.llm.client import LLMClient
from app.llm.embeddings import EmbeddingProvider, get_embedding_provider
from app.db.session import AsyncSessionLocal
from app.db.models import LLMUsage

T = TypeVar("T", bound=BaseModel)

class GenerativeEngineClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        embedding_provider: Optional[EmbeddingProvider] = None
    ):
        self.base_url = (base_url or settings.GENAI_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.GENAI_API_KEY
        self.model = model or settings.GENAI_CHAT_MODEL
        self.embedding_provider = embedding_provider or get_embedding_provider()

    async def _record_usage(
        self,
        ticket_id: Optional[str],
        run_id: Optional[str],
        node: Optional[str],
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int
    ):
        try:
            async with AsyncSessionLocal() as session:
                usage = LLMUsage(
                    ticket_id=ticket_id,
                    run_id=run_id,
                    node=node,
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_ms=latency_ms
                )
                session.add(usage)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to record LLM usage: {e}")

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
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        retries = settings.GENAI_MAX_RETRIES
        delay = 1.0

        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.GENAI_TIMEOUT_SECONDS) as client:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                        await asyncio.sleep(delay)
                        delay *= 2
                        continue
                    resp.raise_for_status()
                    data = resp.json()
                    
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    prompt_tok = usage.get("prompt_tokens", len(str(messages)) // 4)
                    comp_tok = usage.get("completion_tokens", len(content) // 4)
                    latency = int((time.time() - start_time) * 1000)

                    await self._record_usage(ticket_id, run_id, node, prompt_tok, comp_tok, latency)
                    return content
            except Exception as e:
                if attempt == retries:
                    logger.error(f"Generative Engine chat call failed after {retries} retries: {e}")
                    raise
                await asyncio.sleep(delay)
                delay *= 2

        raise RuntimeError("Chat completion failed unexpectedly")

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
        # For simplicity, streaming calls standard chat and yields words or chunks
        text = await self.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            ticket_id=ticket_id,
            run_id=run_id,
            node=node
        )
        words = text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.015)

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
        schema_prompt = (
            f"\nYou must return ONLY a valid JSON object matching this schema:\n"
            f"{json.dumps(schema.model_json_schema(), indent=2)}\n"
            f"Do not include any Markdown code blocks or extraneous text. Output raw JSON only."
        )
        augmented_messages = list(messages)
        augmented_messages[-1] = {
            "role": augmented_messages[-1]["role"],
            "content": augmented_messages[-1]["content"] + schema_prompt
        }

        raw_text = await self.chat(
            augmented_messages,
            temperature=temperature,
            ticket_id=ticket_id,
            run_id=run_id,
            node=node
        )

        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()

        try:
            data = json.loads(clean_text)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            # One repair attempt
            logger.warning(f"JSON validation failed: {e}. Attempting repair call.")
            repair_messages = [
                {"role": "system", "content": "You fix invalid JSON according to the given Pydantic schema."},
                {"role": "user", "content": f"The output:\n{clean_text}\nfailed with error: {str(e)}.\nReturn ONLY the corrected JSON for schema: {schema.model_json_schema()}."}
            ]
            repair_text = await self.chat(repair_messages, temperature=0.0, ticket_id=ticket_id, run_id=run_id, node=node)
            repair_clean = repair_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(repair_clean)
            return schema.model_validate(data)

    async def embed(self, texts: List[str]) -> List[List[float]]:
        return await self.embedding_provider.embed(texts)
