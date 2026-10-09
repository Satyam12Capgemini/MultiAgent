import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from app.core.logging import logger

class BM25Index:
    def __init__(self):
        self.corpus_chunks: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def build_index(self, chunks: List[Dict[str, Any]]):
        """
        Builds or updates BM25 index from a list of dicts:
        { "chunk_id": str, "doc_id": str, "title": str, "category": str, "text": str }
        """
        self.corpus_chunks = chunks
        self.tokenized_corpus = [self._tokenize(c["text"]) for c in chunks]
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            logger.info(f"BM25 index built with {len(chunks)} chunks.")
        else:
            self.bm25 = None

    def query(
        self,
        query_text: str,
        top_k: int = 20,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.corpus_chunks:
            return []

        tokenized_query = self._tokenize(query_text)
        if not tokenized_query:
            return []

        scored_results = []
        if self.bm25:
            doc_scores = self.bm25.get_scores(tokenized_query)
        else:
            doc_scores = [0.0] * len(self.corpus_chunks)

        for idx, score in enumerate(doc_scores):
            chunk = self.corpus_chunks[idx]
            if category and chunk.get("category") != category:
                continue

            # Calculate term match overlap
            tokens_in_chunk = set(self.tokenized_corpus[idx])
            overlap_count = sum(1 for t in tokenized_query if t in tokens_in_chunk)
            
            # Use positive BM25 score or term overlap
            final_score = float(score) if score > 0 else float(overlap_count)
            if final_score > 0:
                scored_results.append({
                    "chunk_id": chunk["chunk_id"],
                    "doc_id": chunk["doc_id"],
                    "title": chunk["title"],
                    "category": chunk.get("category", ""),
                    "text": chunk["text"],
                    "score": final_score
                })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]

bm25_index = BM25Index()
