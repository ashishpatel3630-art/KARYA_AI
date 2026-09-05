from fastapi import status

from app.core.config import settings
import app.core.database as db_module
from app.models.session import Session as UserSession


def login(client, email):
    client.post(
        "/auth/register",
        json={"email": email, "password": "StrongPass123!"},
    )
    return client.post(
        "/auth/login",
        json={"email": email, "password": "StrongPass123!"},
    ).json()


def test_idle_timeout_rejects_refresh_and_revokes_session(client, monkeypatch):
    monkeypatch.setattr(settings, "SESSION_IDLE_TIMEOUT_DAYS", 0)
    tokens = login(client, "idle-timeout@example.com")

    response = client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_absolute_timeout_rejects_refresh(client, monkeypatch):
    monkeypatch.setattr(settings, "SESSION_ABSOLUTE_TIMEOUT_DAYS", 0)
    tokens = login(client, "absolute-timeout@example.com")

    response = client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_session_records_last_used_and_preserves_absolute_deadline(client):
    tokens = login(client, "session-state@example.com")
    db = db_module.SessionLocal()
    try:
        session = db.query(UserSession).one()
        assert session.last_used_at is None
        assert session.absolute_expires_at is not None
        original_deadline = session.absolute_expires_at
    finally:
        db.close()

    refreshed = client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refreshed.status_code == status.HTTP_200_OK

    db = db_module.SessionLocal()
    try:
        sessions = db.query(UserSession).order_by(UserSession.created_at).all()
        assert sessions[-1].absolute_expires_at == original_deadline
        assert sessions[-1].last_used_at is not None
    finally:
        db.close()