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
