import math
import time
from typing import List, Dict, Any, Optional, Tuple

class SemanticVectorCache:
    """
    In-memory Semantic Vector Cache using Cosine Similarity.
    Enables low-latency cache retrieval for LLM embeddings with similarity thresholding.
    """
    def __init__(self, similarity_threshold: float = 0.85, max_entries: int = 1000):
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        # Entries: List of (vector, query_text, response_value, timestamp)
        self.entries: List[Tuple[List[float], str, Any, float]] = []

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def get(self, query_vector: List[float]) -> Optional[Tuple[Any, float]]:
        """
        Looks up vector cache. Returns (cached_value, similarity_score) if above threshold.
        """
        best_match = None
        best_score = -1.0

        for vec, text, val, ts in self.entries:
            sim = self._cosine_similarity(query_vector, vec)
            if sim > best_score:
                best_score = sim
                best_match = val

        if best_score >= self.similarity_threshold:
            return best_match, best_score
        return None

    def set(self, query_vector: List[float], query_text: str, response_value: Any):
        if len(self.entries) >= self.max_entries:
            self.entries.pop(0)  # Evict oldest entry (FIFO)
        self.entries.append((query_vector, query_text, response_value, time.time()))
