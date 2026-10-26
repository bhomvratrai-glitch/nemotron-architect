import time
import pytest
from rate_limiter import TokenBucketRateLimiter

def test_initial_capacity():
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate_per_sec=1.0)
    for _ in range(5):
        assert limiter.allow_request("client_1") is True
    # 6th request rejected
    assert limiter.allow_request("client_1") is False

def test_refill_mechanism():
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate_per_sec=10.0)
    assert limiter.allow_request("client_2") is True
    assert limiter.allow_request("client_2") is True
    assert limiter.allow_request("client_2") is False
    time.sleep(0.2)  # Refills ~2 tokens
    assert limiter.allow_request("client_2") is True
