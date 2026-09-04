from fastapi import status


def test_refresh_reuse_is_rejected(client):
    response = client.post(
        "/auth/register",
        json={"email": "reuse@example.com", "password": "StrongPass123!"},
    )
    assert response.status_code == status.HTTP_201_CREATED

    login = client.post(
        "/auth/login",
        json={"email": "reuse@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == status.HTTP_200_OK

    refresh_token = login.json()["refresh_token"]
    first_refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert first_refresh.status_code == status.HTTP_200_OK

    second_refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert second_refresh.status_code == status.HTTP_401_UNAUTHORIZED
