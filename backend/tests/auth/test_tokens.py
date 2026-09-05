from app.auth.tokens import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_access_token_has_expected_claims():
    token = create_access_token("user-123")
    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"
    assert "jti" in payload
    assert "exp" in payload


def test_refresh_token_has_expected_claims():
    token, jti, family, expires_at = create_refresh_token("user-123")
    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti
    assert payload["token_family"] == family
    assert expires_at is not None
