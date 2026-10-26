import hmac
import hashlib
import base64
import json
import time
from typing import Optional, Dict, Any

class JWTAuthService:
    """
    Self-contained, production-grade JWT Authentication Service.
    Zero external heavy C-dependencies, utilizing HMAC-SHA256 for cryptographic signing.
    """
    def __init__(self, secret_key: str = "nemotron-architect-secure-key-2026", default_expiry_seconds: int = 3600):
        self.secret_key = secret_key.encode("utf-8")
        self.default_expiry = default_expiry_seconds

    def _b64_encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    def _b64_decode(self, data: str) -> bytes:
        padding = "=" * (4 - (len(data) % 4)) if (len(data) % 4) != 0 else ""
        return base64.urlsafe_b64decode((data + padding).encode("utf-8"))

    def create_token(self, subject: str, custom_claims: Optional[Dict[str, Any]] = None, expiry_seconds: Optional[int] = None) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        now = int(time.time())
        exp = now + (expiry_seconds if expiry_seconds is not None else self.default_expiry)
        payload = {"sub": subject, "iat": now, "exp": exp}
        if custom_claims:
            payload.update(custom_claims)

        encoded_header = self._b64_encode(json.dumps(header).encode("utf-8"))
        encoded_payload = self._b64_encode(json.dumps(payload).encode("utf-8"))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")

        signature = hmac.new(self.secret_key, signing_input, hashlib.sha256).digest()
        encoded_sig = self._b64_encode(signature)

        return f"{encoded_header}.{encoded_payload}.{encoded_sig}"

    def verify_token(self, token: str) -> Dict[str, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed token: expected 3 segments")

        encoded_header, encoded_payload, encoded_sig = parts
        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")

        expected_sig = hmac.new(self.secret_key, signing_input, hashlib.sha256).digest()
        provided_sig = self._b64_decode(encoded_sig)

        if not hmac.compare_digest(expected_sig, provided_sig):
            raise ValueError("Invalid cryptographic signature: token has been tampered with")

        payload = json.loads(self._b64_decode(encoded_payload).decode("utf-8"))
        if payload.get("exp") and payload["exp"] < int(time.time()):
            raise ValueError("Token expired")

        return payload
