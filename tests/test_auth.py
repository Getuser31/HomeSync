"""Unit tests for authentication module."""
import pytest
from datetime import datetime, timedelta
from jose import jwt, ExpiredSignatureError

from app.auth import create_access_token, decode_access_token

# Use a fixed known secret key for reproducible testing
TEST_SECRET = "test-secret-key-for-testing-purposes-only"


class TestAuth:
    """Tests for auth functions."""

    def test_create_and_decode_access_token(self):
        token = create_access_token(user_id=1, email="test@example.com")
        user_id, expired = decode_access_token(token)
        assert user_id == 1
        assert expired is False

    def test_decode_expired_token(self):
        """Manually craft an expired token and verify it returns expired=True."""
        payload = {
            "sub": "1",
            "email": "test@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1),
        }
        token = jwt.encode(payload, TEST_SECRET, algorithm="HS256")

        # Temporarily patch the module-level SECRET_KEY
        import app.auth as auth_mod
        original = auth_mod.SECRET_KEY
        auth_mod.SECRET_KEY = TEST_SECRET
        try:
            user_id, expired = decode_access_token(token)
            assert user_id is None
            assert expired is True
        finally:
            auth_mod.SECRET_KEY = original

    def test_decode_invalid_token(self):
        user_id, expired = decode_access_token("invalid-token-here")
        assert user_id is None
        assert expired is False

    def test_decode_malformed_token(self):
        user_id, expired = decode_access_token("this.is.not.a.jwt")
        assert user_id is None
        assert expired is False

    def test_decode_empty_token(self):
        user_id, expired = decode_access_token("")
        assert user_id is None
        assert expired is False

    def test_create_token_with_remember_me(self):
        token = create_access_token(user_id=1, email="test@example.com", remember_me=True)
        user_id, expired = decode_access_token(token)
        assert user_id == 1
        assert expired is False

    def test_decode_token_wrong_secret(self):
        """A token signed with a different secret should be rejected."""
        payload = {
            "sub": "1",
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        token = jwt.encode(payload, "different-secret", algorithm="HS256")
        import app.auth as auth_mod
        original = auth_mod.SECRET_KEY
        auth_mod.SECRET_KEY = TEST_SECRET
        try:
            user_id, expired = decode_access_token(token)
            assert user_id is None
            assert expired is False
        finally:
            auth_mod.SECRET_KEY = original
