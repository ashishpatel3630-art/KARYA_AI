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


def test_register_persists_identity_and_never_trusts_requested_role(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "StrongPass123!",
            "secret_key": "KRYA-7F4A9C-82XP91-4D72AB",
            "role": "admin",
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.post(
        "/auth/register",
        json={
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "StrongPass123!",
            "secret_key": "KRYA-7F4A9C-82XP91-4D72AB",
            "role": "user",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["role"] == "USER"

    login = client.post(
        "/auth/login",
        json={"email": "ada@example.com", "password": "StrongPass123!"},
    )
    profile = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert profile.status_code == status.HTTP_200_OK
    assert profile.json()["name"] == "Ada Lovelace"
    assert profile.json()["role"] == "USER"
    assert "secret_key_hash" not in profile.json()


def test_register_rejects_weak_password(client):
    response = client.post(
        "/auth/register",
        json={"email": "weak@example.com", "password": "short"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
