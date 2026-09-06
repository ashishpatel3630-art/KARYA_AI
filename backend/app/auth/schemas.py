from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(LoginRequest):
    name: str = Field(default="KARYA User", min_length=1, max_length=120)
    secret_key: str | None = Field(default=None, min_length=8, max_length=128)
    role: str = Field(default="user", max_length=30)
    invitation_token: str | None = Field(default=None, min_length=20, max_length=128)


class InvitationRequest(BaseModel):
    role: str = Field(min_length=1, max_length=30)
    email: EmailStr | None = None
    expires_in_hours: int = Field(default=72, ge=1, le=168)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MFAChallengeResponse(BaseModel):
    mfa_required: bool = True
    challenge_token: str
    token_type: str = "bearer"