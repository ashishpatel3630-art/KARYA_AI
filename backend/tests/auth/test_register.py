from fastapi import status


def test_register_creates_user_and_safe_response(client):
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "StrongPass123!"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    payload = response.json()
    assert payload["email"] == "user@example.com"
    assert "password" not in payload
    assert "password_hash" not in payload


def test_register_rejects_duplicate_email(client):
    client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "StrongPass123!"},
    )

    response = client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "StrongPass123!"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
