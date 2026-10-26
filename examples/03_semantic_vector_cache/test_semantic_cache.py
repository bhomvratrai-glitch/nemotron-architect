import pytest
from semantic_cache import SemanticVectorCache

def test_exact_vector_hit():
    cache = SemanticVectorCache(similarity_threshold=0.90)
    vec = [1.0, 0.0, 0.0]
    cache.set(vec, "what is python", "Python is a programming language.")
    result = cache.get([1.0, 0.0, 0.0])
    assert result is not None
    val, score = result
    assert val == "Python is a programming language."
    assert score >= 0.99

def test_semantic_similarity_hit():
    cache = SemanticVectorCache(similarity_threshold=0.85)
    # Target vector
    cache.set([1.0, 0.5, 0.0], "query 1", "answer 1")
    # Slightly rotated vector (high similarity)
    res = cache.get([1.0, 0.45, 0.0])
    assert res is not None
    val, score = res
    assert val == "answer 1"
    assert score > 0.85

def test_orthogonal_miss():
    cache = SemanticVectorCache(similarity_threshold=0.85)
    cache.set([1.0, 0.0, 0.0], "query", "answer")
    # Orthogonal vector (cosine sim = 0)
    assert cache.get([0.0, 1.0, 0.0]) is None
