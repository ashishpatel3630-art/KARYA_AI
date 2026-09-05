from fastapi import status


def test_refresh_rotation_creates_new_token(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "rotation@example.com",
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    login = client.post(
        "/auth/login",
        json={
            "email": "rotation@example.com",
            "password": "StrongPass123!",
        },
    )
    assert login.status_code == status.HTTP_200_OK

    token_a = login.json()["refresh_token"]

    refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": token_a},
    )

    assert refresh.status_code == status.HTTP_200_OK

    token_b = refresh.json()["refresh_token"]

    # Rotation must produce a different refresh token.
    assert token_b != token_a


def test_refresh_reuse_revokes_entire_token_family(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "family@example.com",
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    login = client.post(
        "/auth/login",
        json={
            "email": "family@example.com",
            "password": "StrongPass123!",
        },
    )
    assert login.status_code == status.HTTP_200_OK

    token_a = login.json()["refresh_token"]

    # A -> B
    first_refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": token_a},
    )

    assert first_refresh.status_code == status.HTTP_200_OK

    token_b = first_refresh.json()["refresh_token"]

    # Reuse A.
    replay = client.post(
        "/auth/refresh",
        json={"refresh_token": token_a},
    )

    assert replay.status_code == status.HTTP_401_UNAUTHORIZED
    assert replay.json()["detail"] == "Refresh token reuse detected"

    # Because A was replayed, B should now also be invalid.
    second_refresh = client.post(
        "/auth/refresh",
        json={"refresh_token": token_b},
    )

    assert second_refresh.status_code == status.HTTP_401_UNAUTHORIZED