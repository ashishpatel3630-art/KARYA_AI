from fastapi import status


def test_logout_revokes_current_session(client):
    client.post(
        "/auth/register",
        json={"email": "logout@example.com", "password": "StrongPass123!"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "logout@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == status.HTTP_200_OK

    logout = client.post(
        "/auth/logout",
        json={"refresh_token": login.json()["refresh_token"]},
    )
    assert logout.status_code == status.HTTP_200_OK

    rejected = client.post(
        "/auth/refresh",
        json={"refresh_token": login.json()["refresh_token"]},
    )
    assert rejected.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_revokes_rotated_session_and_rejects_repeated_logout(client):
    client.post(
        "/auth/register",
        json={"email": "rotated-logout@example.com", "password": "StrongPass123!"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "rotated-logout@example.com", "password": "StrongPass123!"},
    )
    old_token = login.json()["refresh_token"]
    rotated = client.post("/auth/refresh", json={"refresh_token": old_token})
    new_token = rotated.json()["refresh_token"]

    logout = client.post("/auth/logout", json={"refresh_token": new_token})
    assert logout.status_code == status.HTTP_200_OK

    assert client.post(
        "/auth/refresh", json={"refresh_token": new_token}
    ).status_code == status.HTTP_401_UNAUTHORIZED
    assert client.post(
        "/auth/logout", json={"refresh_token": new_token}
    ).status_code == status.HTTP_401_UNAUTHORIZED
    assert client.post(
        "/auth/refresh", json={"refresh_token": old_token}
    ).status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_invalid_token_does_not_affect_another_user(client):
    client.post(
        "/auth/register",
        json={"email": "logout-a@example.com", "password": "StrongPass123!"},
    )
    user_a = client.post(
        "/auth/login",
        json={"email": "logout-a@example.com", "password": "StrongPass123!"},
    ).json()
    client.post(
        "/auth/register",
        json={"email": "logout-b@example.com", "password": "StrongPass123!"},
    )
    user_b = client.post(
        "/auth/login",
        json={"email": "logout-b@example.com", "password": "StrongPass123!"},
    ).json()

    invalid_logout = client.post(
        "/auth/logout", json={"refresh_token": user_a["refresh_token"] + "x"}
    )
    assert invalid_logout.status_code == status.HTTP_401_UNAUTHORIZED

    still_valid = client.post(
        "/auth/refresh", json={"refresh_token": user_b["refresh_token"]}
    )
    assert still_valid.status_code == status.HTTP_200_OK
