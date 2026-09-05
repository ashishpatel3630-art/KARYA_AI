from datetime import datetime, timezone

from fastapi import status
from sqlalchemy import select

from app.core.database import get_db
from app.models.session import Session


def test_refresh_updates_last_used_at(client):
    register = client.post(
        "/auth/register",
        json={
            "email": "lastused@example.com",
            "password": "StrongPass123!",
        },
    )

    assert register.status_code == status.HTTP_201_CREATED

    login = client.post(
        "/auth/login",
        json={
            "email": "lastused@example.com",
            "password": "StrongPass123!",
        },
    )

    assert login.status_code == status.HTTP_200_OK

    refresh_token = login.json()["refresh_token"]

    # Get the same database session used by the test client.
    db = next(get_db())

    try:
        session = db.execute(
            select(Session)
            .order_by(Session.created_at.desc())
        ).scalars().first()

        assert session is not None
        assert session.last_used_at is None

        session_id = session.id

    finally:
        db.close()

    # Perform refresh.
    refresh = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh.status_code == status.HTTP_200_OK

    # The refresh helper updates last_used_at.
    # Verify the value on the session object through
    # the same test database dependency.
    db = next(get_db())

    try:
        session = db.get(Session, session_id)

        assert session is not None
        assert session.last_used_at is not None

        last_used = session.last_used_at

        if last_used.tzinfo is None:
            last_used = last_used.replace(
                tzinfo=timezone.utc
            )

        assert last_used <= datetime.now(timezone.utc)

    finally:
        db.close()