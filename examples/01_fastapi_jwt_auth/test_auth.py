import pytest
import time
from auth_service import JWTAuthService

def test_token_creation_and_verification():
    service = JWTAuthService(secret_key="test-secret")
    token = service.create_token(subject="user_123", custom_claims={"role": "admin"})
    payload = service.verify_token(token)
    assert payload["sub"] == "user_123"
    assert payload["role"] == "admin"

def test_tampered_signature_rejection():
    service = JWTAuthService(secret_key="test-secret")
    token = service.create_token(subject="user_123")
    parts = token.split(".")
    # Tamper with payload
    tampered_payload = "eyJzdWIiOiAiaGFja2VyIn0"
    tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"
    with pytest.raises(ValueError, match="Invalid cryptographic signature"):
        service.verify_token(tampered_token)

def test_expired_token_rejection():
    service = JWTAuthService(secret_key="test-secret")
    # Expire 10 seconds ago
    token = service.create_token(subject="user_123", expiry_seconds=-10)
    with pytest.raises(ValueError, match="Token expired"):
        service.verify_token(token)
