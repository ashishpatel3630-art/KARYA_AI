import base64
import hashlib
import hmac
import struct
import time

from fastapi import status


def totp_code(secret):
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    counter = int(time.time()) // 30
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"


def setup_mfa(client):
    client.post(
        "/auth/register",
        json={"email": "mfa-flow@example.com", "password": "StrongPass123!"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "mfa-flow@example.com", "password": "StrongPass123!"},
    )
    access = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {access}"}
    enroll = client.post("/mfa/totp/enroll", headers=headers)
    secret = enroll.json()["secret"]
    enable = client.post(
        "/mfa/totp/enable",
        headers=headers,
        json={"code": totp_code(secret)},
    )
    assert enable.status_code == status.HTTP_200_OK
    return secret


def test_mfa_login_requires_challenge_completion(client):
    secret = setup_mfa(client)

    login = client.post(
        "/auth/login",
        json={"email": "mfa-flow@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == status.HTTP_200_OK
    payload = login.json()
    assert payload["mfa_required"] is True
    assert "access_token" not in payload
    assert "refresh_token" not in payload

    invalid = client.post(
        "/mfa/totp/challenge",
        json={"challenge_token": payload["challenge_token"], "code": "000000"},
    )
    assert invalid.status_code == status.HTTP_401_UNAUTHORIZED

    completed = client.post(
        "/mfa/totp/challenge",
        json={
            "challenge_token": payload["challenge_token"],
            "code": totp_code(secret),
        },
    )
    assert completed.status_code == status.HTTP_200_OK
    assert "access_token" in completed.json()
    assert "refresh_token" in completed.json()