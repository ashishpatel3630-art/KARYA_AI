import jwt
from fastapi import status

from app.auth.tokens import decode_token
from app.core.config import settings


def test_refresh_token_contains_session_binding_claims(client):
    register = client.post(
        "/auth/register",
        json={
            "email": "binding@example.com",
            "password": "StrongPass123!",
        },
    )

    assert register.status_code == status.HTTP_201_CREATED

    login = client.post(
        "/auth/login",
        json={
            "email": "binding@example.com",
            "password": "StrongPass123!",
        },
    )

    assert login.status_code == status.HTTP_200_OK

    refresh_token = login.json()["refresh_token"]

    payload = decode_token(refresh_token)

    assert payload["type"] == "refresh"
    assert payload["sub"]
    assert payload["jti"]
    assert payload["token_family"]


def test_refresh_rejects_jti_session_mismatch(client):
    register = client.post(
        "/auth/register",
        json={
            "email": "jti-mismatch@example.com",
            "password": "StrongPass123!",
        },
    )

    assert register.status_code == status.HTTP_201_CREATED

    login = client.post(
        "/auth/login",
        json={
            "email": "jti-mismatch@example.com",
            "password": "StrongPass123!",
        },
    )

    assert login.status_code == status.HTTP_200_OK

    refresh_token = login.json()["refresh_token"]

    payload = decode_token(refresh_token)

    forged_payload = dict(payload)
    forged_payload["jti"] = "00000000-0000-0000-0000-000000000000"

    forged_token = jwt.encode(
        forged_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": forged_token,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Refresh session not found"


def test_refresh_rejects_token_family_session_mismatch(client):
    register = client.post(
        "/auth/register",
        json={
            "email": "family-mismatch@example.com",
            "password": "StrongPass123!",
        },
    )

    assert register.status_code == status.HTTP_201_CREATED

    login = client.post(
        "/auth/login",
        json={
            "email": "family-mismatch@example.com",
            "password": "StrongPass123!",
        },
    )

    assert login.status_code == status.HTTP_200_OK

    refresh_token = login.json()["refresh_token"]

    payload = decode_token(refresh_token)

    forged_payload = dict(payload)
    forged_payload["token_family"] = (
        "00000000-0000-0000-0000-000000000000"
    )

    forged_token = jwt.encode(
        forged_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": forged_token,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Refresh session not found"
