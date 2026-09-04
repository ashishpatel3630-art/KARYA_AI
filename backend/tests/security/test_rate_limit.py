from fastapi import status


def test_register_is_not_blocked_on_first_attempt(client):
    response = client.post(
        "/auth/register",
        json={"email": "rate@example.com", "password": "StrongPass123!"},
    )

    assert response.status_code == status.HTTP_201_CREATED
