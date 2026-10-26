import time
import threading
from typing import Dict, Tuple

class TokenBucketRateLimiter:
    """
    High-concurrency thread-safe Token Bucket Rate Limiter.
    Allows microsecond rate limiting with configurable capacity and refill rates.
    """
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        # Maps client_id -> (current_tokens: float, last_updated: float)
        self.buckets: Dict[str, Tuple[float, float]] = {}
        self.lock = threading.Lock()

    def allow_request(self, client_id: str, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            if client_id not in self.buckets:
                self.buckets[client_id] = (float(self.capacity), now)

            current_tokens, last_refill = self.buckets[client_id]
            elapsed = now - last_refill
            # Refill tokens
            new_tokens = min(float(self.capacity), current_tokens + (elapsed * self.refill_rate))

            if new_tokens >= tokens:
                self.buckets[client_id] = (new_tokens - tokens, now)
                return True
            else:
                self.buckets[client_id] = (new_tokens, now)
                return False
