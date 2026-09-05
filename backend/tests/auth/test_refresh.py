from fastapi import status


def test_refresh_rotates_refresh_token(client):
    client.post(
        "/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "StrongPass123!",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "StrongPass123!",
        },
    )

    assert login_response.status_code == status.HTTP_200_OK

    tokens = login_response.json()

    old_refresh_token = tokens["refresh_token"]

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token,
        },
    )

    assert refresh_response.status_code == status.HTTP_200_OK

    new_tokens = refresh_response.json()

    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

    assert new_tokens["refresh_token"] != old_refresh_token