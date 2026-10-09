from typing import List, Dict, Any

def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: int = 60,
    top_k: int = 4
) -> List[Dict[str, Any]]:
    """
    Combines vector and BM25 search rankings using Reciprocal Rank Fusion (RRF).
    """
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, Dict[str, Any]] = {}
    vector_scores: Dict[str, float] = {}
    bm25_scores: Dict[str, float] = {}

    # Rank vector results (1-indexed)
    for rank, item in enumerate(vector_results, 1):
        cid = item["chunk_id"]
        chunk_map[cid] = item
        vector_scores[cid] = item.get("score", 0.0)
        scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank))

    # Rank BM25 results (1-indexed)
    for rank, item in enumerate(bm25_results, 1):
        cid = item["chunk_id"]
        if cid not in chunk_map:
            chunk_map[cid] = item
        bm25_scores[cid] = item.get("score", 0.0)
        scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank))

    # Compile combined results
    fused: List[Dict[str, Any]] = []
    for cid, rrf_score in scores.items():
        base = dict(chunk_map[cid])
        base["score"] = rrf_score
        base["vector_score"] = vector_scores.get(cid)
        base["bm25_score"] = bm25_scores.get(cid)
        fused.append(base)

    fused.sort(key=lambda x: x["score"], reverse=True)
    return fused[:top_k]
