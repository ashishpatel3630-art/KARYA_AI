import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, status

from app.core.config import settings
from app.core.redis import get_redis


router = APIRouter(prefix="/oauth", tags=["OAuth"])

_PROVIDER_AUTH_URLS = {
    "google": "https://accounts.google.com/o/oauth2/v2/auth",
    "github": "https://github.com/login/oauth/authorize",
    "microsoft": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
}
_PROVIDER_CLIENT_SETTINGS = {
    "google": "GOOGLE_CLIENT_ID",
    "github": "GITHUB_CLIENT_ID",
    "microsoft": "MICROSOFT_CLIENT_ID",
}


@router.get("/{provider}/authorize")
def authorize(provider: str, redirect_uri: str):
    provider = provider.lower()
    if provider not in _PROVIDER_AUTH_URLS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unsupported OAuth provider")

    client_id = getattr(settings, _PROVIDER_CLIENT_SETTINGS[provider])
    if not client_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OAuth provider is not configured")

    state = secrets.token_urlsafe(32)
    get_redis().setex(
        f"oauth_state:{state}",
        settings.OAUTH_STATE_TTL_SECONDS,
        f"{provider}|{redirect_uri}",
    )
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile" if provider != "github" else "read:user user:email",
        "state": state,
    }
    return {"authorization_url": f"{_PROVIDER_AUTH_URLS[provider]}?{urlencode(params)}"}


@router.get("/{provider}/callback")
def callback(provider: str, code: str = Query(min_length=1), state: str = Query(min_length=1)):
    provider = provider.lower()
    stored = get_redis().getdel(f"oauth_state:{state}")
    if stored is None or not stored.startswith(f"{provider}|"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")
    return {"message": "OAuth callback validated", "provider": provider, "code": code}
