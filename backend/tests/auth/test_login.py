from fastapi import status


def test_login_returns_tokens(client):
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "StrongPass123!"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "StrongPass123!"},
    )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert "access_token" in payload
    assert "refresh_token" in payload
    assert payload["token_type"] == "bearer"


def test_login_rejects_invalid_password(client):
    client.post(
        "/auth/register",
        json={"email": "wrong@example.com", "password": "StrongPass123!"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "wrong@example.com", "password": "WrongPassword1!"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
