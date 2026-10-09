from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.llm.factory import get_llm_client
from app.rag.chroma_store import chroma_store
from app.rag.bm25 import bm25_index
from app.rag.fusion import reciprocal_rank_fusion
from app.core.logging import logger

class HybridRetriever:
    async def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 4,
        mode: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Retrieves most relevant chunks using hybrid (vector + BM25) search.
        """
        llm = get_llm_client()
        
        # 1. Vector Search
        vector_results = []
        if mode in ("hybrid", "vector"):
            try:
                embeddings = await llm.embed([query])
                if embeddings:
                    vector_results = chroma_store.query(
                        query_embedding=embeddings[0],
                        top_k=20,
                        category=category
                    )
            except Exception as e:
                logger.error(f"Vector search failed: {e}")

        # 2. BM25 Search
        bm25_results = []
        if mode in ("hybrid", "bm25"):
            bm25_results = bm25_index.query(
                query_text=query,
                top_k=20,
                category=category
            )

        # 3. Fusion & Ranking
        if mode == "vector":
            results = vector_results[:top_k]
        elif mode == "bm25":
            results = bm25_results[:top_k]
        else:
            results = reciprocal_rank_fusion(
                vector_results=vector_results,
                bm25_results=bm25_results,
                k=60,
                top_k=top_k
            )

        return results

    def build_context_block(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Wraps chunks in untrusted data tags <context id="n">...</context>.
        """
        if not chunks:
            return ""

        blocks = []
        for i, chunk in enumerate(chunks, 1):
            title = chunk.get("title", "Document")
            cid = chunk.get("chunk_id", f"c-{i}")
            text = chunk.get("text", "").strip()
            blocks.append(f'<context id="{i}" source="{title}" chunk="{cid}">\n{text}\n</context>')

        return "\n\n".join(blocks)

retriever = HybridRetriever()
