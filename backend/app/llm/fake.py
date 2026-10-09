import asyncio
import json
import re
from typing import List, Dict, Any, Optional, TypeVar, AsyncIterator
from pydantic import BaseModel
from app.llm.client import LLMClient
from app.llm.embeddings import FakeEmbeddingProvider
from app.db.session import AsyncSessionLocal
from app.db.models import LLMUsage
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)

class FakeLLMClient:
    """Realistic offline mock LLM client for seamless local development and tests."""
    def __init__(self):
        self.embedding_provider = FakeEmbeddingProvider()

    async def _record_usage(self, ticket_id: Optional[str], run_id: Optional[str], node: Optional[str], prompt_tokens: int, completion_tokens: int):
        try:
            async with AsyncSessionLocal() as session:
                usage = LLMUsage(
                    ticket_id=ticket_id,
                    run_id=run_id,
                    node=node,
                    model="fake-engine-v1",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_ms=120
                )
                session.add(usage)
                await session.commit()
        except Exception as e:
            logger.debug(f"Fake LLM usage logging skipped: {e}")

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
        await asyncio.sleep(0.05)
        user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_msg = m["content"]
                break

        await self._record_usage(ticket_id, run_id, node, len(str(messages)) // 4, 80)

        # Context-based response generation
        if "<context" in user_msg:
            # Extract citation contexts
            contexts = re.findall(r'<context id="(\d+)" source="([^"]+)">(.*?)</context>', user_msg, re.DOTALL)
            if contexts:
                primary_id, primary_source, primary_text = contexts[0]
                summary = primary_text.strip().split("\n")[0][:180]
                return f"Based on the {primary_source}, {summary} [{primary_id}]."
            return "I do not have enough information in the provided context to answer your question."

        # Order / billing tool answers
        if "ORD-" in user_msg:
            return "I have reviewed your order details. Your order has been processed and your account status is up to date."

        return "Thank you for contacting support. I have reviewed your request and will assist you right away."

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
        full_text = await self.chat(messages, temperature=temperature, max_tokens=max_tokens, ticket_id=ticket_id, run_id=run_id, node=node)
        words = full_text.split(" ")
        for i, w in enumerate(words):
            yield w + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.01)

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
        await asyncio.sleep(0.05)
        user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_msg = m["content"]
                break

        await self._record_usage(ticket_id, run_id, node, len(str(messages)) // 4, 50)
        schema_name = schema.__name__

        # Handle Classifier Output
        if "Classify" in schema_name or "category" in schema.model_fields:
            lower = user_msg.lower()
            # Sentiment check
            sentiment = "neutral"
            if any(w in lower for w in ["angry", "furious", "terrible", "unacceptable", "scam", "worst", "sue"]):
                sentiment = "angry"
            elif any(w in lower for w in ["bad", "frustrated", "disappointed", "slow", "broken"]):
                sentiment = "negative"

            # Category check
            if any(w in lower for w in ["refund", "charge", "charged", "billing", "invoice", "payment", "ord-", "money", "price"]):
                category = "billing"
                conf = 0.95
                reasoning = "Query mentions billing, orders, refunds or charges."
            elif any(w in lower for w in ["wifi", "router", "firmware", "reboot", "restart", "login", "error", "connection", "bug", "crash"]):
                category = "tech"
                conf = 0.92
                reasoning = "Technical troubleshooting keywords detected."
            elif any(w in lower for w in ["return", "policy", "hours", "contact", "support", "faq", "terms", "shipping"]):
                category = "general"
                conf = 0.88
                reasoning = "General policy and FAQ keywords detected."
            elif any(w in lower for w in ["human", "agent", "representative", "person"]):
                category = "general"
                conf = 0.40  # low confidence to trigger escalation
                reasoning = "User requested a human representative."
            else:
                category = "general"
                conf = 0.55  # lower confidence fallback
                reasoning = "Uncertain classification; fallback to general."

            return schema.model_validate({
                "category": category,
                "confidence": conf,
                "sentiment": sentiment,
                "reasoning": reasoning
            })

        # Handle Critic Output
        if "Critic" in schema_name or "claims" in schema.model_fields:
            if "not have enough information" in user_msg:
                return schema.model_validate({
                    "claims": [{"text": "Agent acknowledged lack of context", "verdict": "SUPPORTED", "source": "Context"}],
                    "score": 1.0,
                    "feedback": []
                })
            
            # Extract citations or claims
            has_citations = bool(re.search(r'\[\d+\]', user_msg))
            if has_citations:
                return schema.model_validate({
                    "claims": [
                        {"text": "Primary fact matches retrieved context", "verdict": "SUPPORTED", "source": "[1]"}
                    ],
                    "score": 1.0,
                    "feedback": []
                })
            else:
                return schema.model_validate({
                    "claims": [
                        {"text": "Answer provides factual guidance without explicit citations", "verdict": "PARTIAL", "source": None}
                    ],
                    "score": 0.5,
                    "feedback": ["Add specific citation markers [1] matching retrieved documentation."]
                })

        # Handle Billing Tool Actions JSON if applicable
        if "action" in schema.model_fields:
            if "refund" in user_msg.lower():
                return schema.model_validate({
                    "action": "issue_refund",
                    "order_id": "ORD-10023",
                    "amount": 299.0,
                    "reason": "Customer request"
                })
            return schema.model_validate({
                "action": "final",
                "answer": "Your request has been processed."
            })

        # Fallback empty construction
        return schema.model_construct()

    async def embed(self, texts: List[str]) -> List[List[float]]:
        return await self.embedding_provider.embed(texts)
