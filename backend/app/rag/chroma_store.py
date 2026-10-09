import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logging import logger

class ChromaStore:
    def __init__(self):
        os.makedirs(settings.CHROMA_PATH, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PATH,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_chunks(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        documents: List[str]
    ):
        if not chunk_ids:
            return
        self.collection.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 20,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        where_filter = {"category": category} if category else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        output = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for i in range(len(ids)):
                # Convert cosine distance to cosine similarity score: 1.0 - distance
                dist = distances[i] if distances else 0.5
                score = max(0.0, min(1.0, 1.0 - dist))
                output.append({
                    "chunk_id": ids[i],
                    "doc_id": metas[i].get("doc_id", ""),
                    "title": metas[i].get("title", ""),
                    "category": metas[i].get("category", ""),
                    "text": docs[i],
                    "score": score
                })
        return output

    def delete_by_doc_id(self, doc_id: str):
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            logger.warning(f"Chroma delete by doc_id error: {e}")

    def count(self) -> int:
        return self.collection.count()

chroma_store = ChromaStore()
