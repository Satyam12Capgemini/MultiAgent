import pytest
from app.rag.chunker import chunker
from app.rag.bm25 import bm25_index
from app.rag.fusion import reciprocal_rank_fusion

def test_chunker_markdown_sections():
    markdown_doc = """# Header 1
This is the first paragraph with important setup instructions.

## Header 2
This is the second section explaining reset pinhole procedure.
"""
    chunks = chunker.split_text(markdown_doc)
    assert len(chunks) >= 1
    assert any("Header 1" in c or "first paragraph" in c for c in chunks)

def test_bm25_index_and_query():
    sample_chunks = [
        {"chunk_id": "c-1", "doc_id": "d-1", "title": "Router Guide", "category": "tech", "text": "Press the reset pinhole button for 10 seconds."},
        {"chunk_id": "c-2", "doc_id": "d-2", "title": "Billing FAQ", "category": "billing", "text": "Refunds take 3 to 5 business days to appear on your bank statement."}
    ]
    bm25_index.build_index(sample_chunks)
    
    tech_results = bm25_index.query("reset button", top_k=2)
    assert len(tech_results) > 0
    assert tech_results[0]["chunk_id"] == "c-1"

def test_rrf_fusion():
    vector_results = [
        {"chunk_id": "c-1", "score": 0.9, "title": "Doc A", "text": "..."},
        {"chunk_id": "c-2", "score": 0.8, "title": "Doc B", "text": "..."}
    ]
    bm25_results = [
        {"chunk_id": "c-2", "score": 12.0, "title": "Doc B", "text": "..."},
        {"chunk_id": "c-3", "score": 8.0, "title": "Doc C", "text": "..."}
    ]
    fused = reciprocal_rank_fusion(vector_results, bm25_results, k=60, top_k=3)
    assert len(fused) == 3
    # c-2 appears in both rankings, should be ranked #1
    assert fused[0]["chunk_id"] == "c-2"
