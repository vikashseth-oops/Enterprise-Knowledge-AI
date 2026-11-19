from typing import Any


class Reranker:
    """
    Reranks and fuses retrieved candidate chunks using Reciprocal Rank Fusion (RRF)
    and cosine score normalization.
    """

    @staticmethod
    def reciprocal_rank_fusion(
        dense_results: list[dict[str, Any]],
        sparse_results: list[dict[str, Any]],
        k: int = 60,
        top_n: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Combines ranked lists from dense vector search and sparse BM25 search
        using Reciprocal Rank Fusion (RRF).
        """
        scores: dict[str, float] = {}
        item_map: dict[str, dict[str, Any]] = {}

        # Process dense rankings
        for rank, item in enumerate(dense_results, start=1):
            chunk_id = item["chunk_id"]
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (k + rank))
            if chunk_id not in item_map:
                item_map[chunk_id] = item

        # Process sparse rankings
        for rank, item in enumerate(sparse_results, start=1):
            chunk_id = item["chunk_id"]
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (k + rank))
            if chunk_id not in item_map:
                item_map[chunk_id] = item

        # Sort by fused RRF score descending
        sorted_chunk_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

        final_results = []
        for cid in sorted_chunk_ids[:top_n]:
            entry = dict(item_map[cid])
            entry["rrf_score"] = round(scores[cid], 5)
            # Retain or blend the original score
            entry["score"] = round(entry.get("score", 0.0), 4)
            final_results.append(entry)

        return final_results
