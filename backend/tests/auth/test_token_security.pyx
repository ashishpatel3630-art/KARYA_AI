
def test_access_token_can_access_current_user(client):
    # Register a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert register_response.status_code in {200, 201}

    # Login
    login_response = client.post(
        "/auth/login",
        json={
            "email": "security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "security@example.com"


def test_refresh_token_cannot_access_current_user(client):
    # Register a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "refresh-security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert register_response.status_code in {200, 201}

    # Login
    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh-security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    # Try using refresh token as an access token
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {refresh_token}",
        },
    )

    assert response.status_code == 401
def test_access_token_can_access_current_user(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert register_response.status_code in {200, 201}

    login_response = client.post(
        "/auth/login",
        json={
            "email": "security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "security@example.com"


def test_refresh_token_cannot_access_current_user(client):
    register_response = client.post(
        "/auth/register",
        json={
            "email": "refresh-security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert register_response.status_code in {200, 201}

    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh-security@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {refresh_token}",
        },
    )

    assert response.status_code == 401
