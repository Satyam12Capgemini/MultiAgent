from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import KBDocument, KBChunk
from app.rag.ingest import ingestion_service
from app.rag.chroma_store import chroma_store
from app.rag.retriever import retriever
from app.core.errors import NotFoundError

class KBService:
    async def list_documents(self, session: AsyncSession) -> List[KBDocument]:
        result = await session.execute(select(KBDocument).order_by(desc(KBDocument.created_at)))
        return list(result.scalars().all())

    async def get_document(self, session: AsyncSession, doc_id: str) -> Optional[KBDocument]:
        result = await session.execute(select(KBDocument).where(KBDocument.id == doc_id))
        doc = result.scalar_one_or_none()
        if not doc:
            raise NotFoundError(f"Document {doc_id} not found")
        return doc

    async def get_document_chunks(self, session: AsyncSession, doc_id: str) -> List[KBChunk]:
        result = await session.execute(
            select(KBChunk).where(KBChunk.doc_id == doc_id).order_by(KBChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def upload_document(
        self,
        session: AsyncSession,
        title: str,
        category: str,
        filename: str,
        content: bytes,
        source: Optional[str] = None
    ) -> KBDocument:
        return await ingestion_service.ingest_document(
            session=session,
            title=title,
            category=category,
            filename=filename,
            content=content,
            source=source
        )

    async def delete_document(self, session: AsyncSession, doc_id: str):
        await ingestion_service.delete_document(session, doc_id)

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        top_k: int = 4,
        mode: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        return await retriever.retrieve(query=query, category=category, top_k=top_k, mode=mode)

    async def reconcile(self, session: AsyncSession) -> Dict[str, Any]:
        """
        Detects and reports drift between MSSQL kb_chunks and ChromaDB vectors.
        """
        # 1. Fetch all chunk IDs in MSSQL
        result = await session.execute(select(KBChunk.id))
        db_chunk_ids = set(result.scalars().all())

        # 2. Get Chroma count
        chroma_count = chroma_store.count()

        return {
            "mssql_chunks_count": len(db_chunk_ids),
            "chroma_vectors_count": chroma_count,
            "in_sync": len(db_chunk_ids) == chroma_count
        }

kb_service = KBService()
