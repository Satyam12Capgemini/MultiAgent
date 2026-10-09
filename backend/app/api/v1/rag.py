import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.schemas.kb import RAGAskRequest, RAGAskResponse, RAGCitation
from app.rag.retriever import retriever
from app.llm.factory import get_llm_client
from app.api.deps import require_roles

router = APIRouter()

@router.post("/ask", response_model=RAGAskResponse)
async def ask_rag(
    req: RAGAskRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin", "agent"]))
):
    start_t = time.time()
    chunks = await retriever.retrieve(query=req.question, category=req.category, top_k=4)
    context_block = retriever.build_context_block(chunks)

    prompt = f"Answer the user query strictly using the context:\n{context_block}\n\nQuery: {req.question}"
    messages = [
        {"role": "system", "content": "Answer with citations [1], [2] based strictly on context."},
        {"role": "user", "content": prompt}
    ]

    llm = get_llm_client()
    answer = await llm.chat(messages, temperature=0.2)
    latency = int((time.time() - start_t) * 1000)

    citations = [
        RAGCitation(n=i, chunk_id=c["chunk_id"], title=c["title"])
        for i, c in enumerate(chunks, 1)
    ]

    return RAGAskResponse(
        answer=answer,
        citations=citations,
        latency_ms=latency
    )
