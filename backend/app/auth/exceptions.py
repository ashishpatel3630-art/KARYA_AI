from fastapi import HTTPException, status


invalid_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid email or password",
    headers={"WWW-Authenticate": "Bearer"},
)


account_temporarily_locked = HTTPException(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    detail="Too many failed login attempts. Try again later.",
)