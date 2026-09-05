import redis
import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.security.rate_limit import enforce_auth_rate_limit


def register_user(client, email="rate-limit@example.com"):
    return client.post(
        "/auth/register",
        json={"email": email, "password": "StrongPass123!"},
    )


def test_login_account_rate_limit_is_independent(client, monkeypatch):
    monkeypatch.setattr(settings, "AUTH_LOGIN_IP_RATE_LIMIT", 10)
    monkeypatch.setattr(settings, "AUTH_LOGIN_ACCOUNT_RATE_LIMIT", 2)
    register_user(client)

    for _ in range(2):
        response = client.post(
            "/auth/login",
            json={
                "email": "rate-limit@example.com",
                "password": "WrongPassword1!",
            },
        )
        assert response.status_code == 401

    response = client.post(
        "/auth/login",
        json={
            "email": "rate-limit@example.com",
            "password": "WrongPassword1!",
        },
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"
    assert "remaining" not in response.text.lower()


def test_login_ip_rate_limit_is_independent(client, monkeypatch):
    monkeypatch.setattr(settings, "AUTH_LOGIN_IP_RATE_LIMIT", 2)
    monkeypatch.setattr(settings, "AUTH_LOGIN_ACCOUNT_RATE_LIMIT", 10)
    register_user(client, "ip-rate-limit@example.com")

    for email in ("one@example.com", "two@example.com"):
        response = client.post(
            "/auth/login",
            json={"email": email, "password": "WrongPassword1!"},
        )
        assert response.status_code == 401

    response = client.post(
        "/auth/login",
        json={"email": "three@example.com", "password": "WrongPassword1!"},
    )

    assert response.status_code == 429


def test_register_rate_limit(client, monkeypatch):
    monkeypatch.setattr(settings, "AUTH_REGISTER_RATE_LIMIT", 1)
    assert register_user(client, "first@example.com").status_code == 201

    response = register_user(client, "second@example.com")

    assert response.status_code == 429


def test_refresh_and_logout_rate_limits(client, monkeypatch):
    monkeypatch.setattr(settings, "AUTH_REFRESH_RATE_LIMIT", 1)
    monkeypatch.setattr(settings, "AUTH_LOGOUT_RATE_LIMIT", 1)
    register_user(client, "refresh-rate-limit@example.com")
    login = client.post(
        "/auth/login",
        json={
            "email": "refresh-rate-limit@example.com",
            "password": "StrongPass123!",
        },
    )
    refresh_token = login.json()["refresh_token"]

    assert client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    ).status_code == 200
    assert client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    ).status_code == 429

    logout_login = client.post(
        "/auth/login",
        json={
            "email": "refresh-rate-limit@example.com",
            "password": "StrongPass123!",
        },
    )
    logout_token = logout_login.json()["refresh_token"]
    assert client.post(
        "/auth/logout", json={"refresh_token": logout_token}
    ).status_code == 200
    assert client.post(
        "/auth/logout", json={"refresh_token": logout_token}
    ).status_code == 429


def test_auth_rate_limit_fails_closed_when_redis_is_unavailable(client, monkeypatch):
    def unavailable_redis():
        raise redis.RedisError("redis unavailable")

    monkeypatch.setattr("app.security.rate_limit.get_redis", unavailable_redis)

    with pytest.raises(HTTPException) as error:
        enforce_auth_rate_limit("register:ip:test", 1)

    assert error.value.status_code == 503
    assert error.value.detail == "Authentication service temporarily unavailable"
