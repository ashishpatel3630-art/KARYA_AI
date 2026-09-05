
import jwt
from datetime import datetime, timedelta, timezone

from app.auth.tokens import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings


def test_access_token_has_required_claims():
    token = create_access_token("user-123")

    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert payload["jti"]
    assert payload["iat"]
    assert payload["exp"]


def test_refresh_token_has_required_claims():
    token, jti, family, expires_at = create_refresh_token("user-123")

    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti
    assert payload["token_family"] == family
    assert payload["iat"]
    assert payload["exp"]


def test_access_token_and_refresh_token_are_different():
    access_token = create_access_token("user-123")
    refresh_token, _, _, _ = create_refresh_token("user-123")

    assert access_token != refresh_token


def test_tampered_token_is_rejected():
    token = create_access_token("user-123")

    header, payload, signature = token.split(".")

    tampered_signature = (
        "A" if signature[0] != "A" else "B"
    )

    tampered_token = ".".join(
        [header, payload, tampered_signature + signature[1:]]
    )

    try:
        decode_token(tampered_token)
        assert False, "Tampered token should be rejected"
    except jwt.PyJWTError:
        pass


def test_expired_token_is_rejected():
    now = datetime.now(timezone.utc)

    payload = {
        "sub": "user-123",
        "jti": "test-jti",
        "type": "access",
        "iat": int((now - timedelta(minutes=10)).timestamp()),
        "exp": int((now - timedelta(minutes=5)).timestamp()),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    try:
        decode_token(token)
        assert False, "Expired token should be rejected"
    except jwt.ExpiredSignatureError:
        pass


def test_invalid_token_type_is_rejected():
    now = datetime.now(timezone.utc)

    payload = {
        "sub": "user-123",
        "jti": "test-jti",
        "type": "invalid",
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=10)).timestamp()
        ),
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    try:
        decode_token(token)
        assert False, "Invalid token type should be rejected"
    except ValueError:
        pass


def test_access_token_can_access_current_user(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert register_response.status_code in {200, 201}

    login_response = client.post(
        "/auth/login",
        json={
            "email": "security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "security@example.com"


def test_refresh_token_cannot_access_current_user(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "refresh-security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert register_response.status_code in {200, 201}

    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh-security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {refresh_token}",
        },
    )

    assert response.status_code == 401
