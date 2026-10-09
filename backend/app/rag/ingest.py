import hashlib
import os
import io
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.models import KBDocument, KBChunk
from app.rag.chunker import chunker
from app.rag.chroma_store import chroma_store
from app.rag.bm25 import bm25_index
from app.llm.factory import get_llm_client
from app.core.logging import logger

def compute_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def extract_text_from_file(filename: str, content: bytes) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".md", ".txt"):
        return content.decode("utf-8", errors="ignore")
    elif ext in (".html", ".htm"):
        soup = BeautifulSoup(content.decode("utf-8", errors="ignore"), "html.parser")
        # Remove script and style elements
        for s in soup(["script", "style"]):
            s.decompose()
        return soup.get_text(separator="\n")
    elif ext == ".pdf":
        reader = PdfReader(io.BytesIO(content))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
        return "\n\n".join(pages_text)
    else:
        return content.decode("utf-8", errors="ignore")

class IngestionService:
    async def ingest_document(
        self,
        session: AsyncSession,
        title: str,
        category: str,
        filename: str,
        content: bytes,
        source: Optional[str] = None
    ) -> KBDocument:
        file_hash = compute_hash(content)
        raw_text = extract_text_from_file(filename, content)
        
        # Create or update document row
        doc = KBDocument(
            title=title,
            category=category,
            source=source or filename,
            file_hash=file_hash,
            status="processing",
            chunk_count=0
        )
        session.add(doc)
        await session.flush()  # get doc.id

        try:
            # 1. Chunk document
            chunks_text = chunker.split_text(raw_text)
            if not chunks_text:
                chunks_text = [raw_text[:1000]] if raw_text.strip() else ["Empty document."]

            chunk_records: List[KBChunk] = []
            chunk_ids: List[str] = []
            metadatas: List[Dict[str, Any]] = []

            for idx, ctext in enumerate(chunks_text):
                chunk = KBChunk(
                    doc_id=doc.id,
                    chunk_index=idx,
                    text=ctext,
                    token_count=len(ctext) // 4
                )
                session.add(chunk)
                chunk_records.append(chunk)

            await session.flush()

            for chunk in chunk_records:
                chunk_ids.append(chunk.id)
                metadatas.append({
                    "doc_id": doc.id,
                    "title": title,
                    "category": category,
                    "source": source or filename,
                    "chunk_index": chunk.chunk_index
                })

            # 2. Embed chunks
            llm = get_llm_client()
            embeddings = await llm.embed(chunks_text)

            # 3. Upsert to Chroma
            chroma_store.upsert_chunks(
                chunk_ids=chunk_ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=chunks_text
            )

            # 4. Update Document status
            doc.chunk_count = len(chunks_text)
            doc.status = "indexed"
            await session.commit()

            # 5. Refresh BM25 Index
            await self.refresh_bm25_index(session)
            return doc

        except Exception as e:
            logger.error(f"Ingestion failed for doc {doc.id}: {e}")
            doc.status = "failed"
            doc.error = str(e)
            await session.commit()
            raise

    async def delete_document(self, session: AsyncSession, doc_id: str):
        # 1. Delete Chroma vectors
        chroma_store.delete_by_doc_id(doc_id)
        
        # 2. Delete database rows
        result = await session.execute(select(KBDocument).where(KBDocument.id == doc_id))
        doc = result.scalar_one_or_none()
        if doc:
            await session.delete(doc)
            await session.commit()

        # 3. Refresh BM25
        await self.refresh_bm25_index(session)

    async def refresh_bm25_index(self, session: AsyncSession):
        result = await session.execute(
            select(KBChunk, KBDocument.title, KBDocument.category)
            .join(KBDocument, KBChunk.doc_id == KBDocument.id)
            .where(KBDocument.status == "indexed")
        )
        rows = result.all()
        chunks_data = []
        for chunk, title, cat in rows:
            chunks_data.append({
                "chunk_id": chunk.id,
                "doc_id": chunk.doc_id,
                "title": title,
                "category": cat,
                "text": chunk.text
            })
        bm25_index.build_index(chunks_data)

ingestion_service = IngestionService()
