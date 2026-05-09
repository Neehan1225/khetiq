from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

# ── Constants ──────────────────────────────────────────────────────────────────
SECRET_KEY: str = settings.secret_key
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS: int = 24

# HTTPBearer extractor – auto-returns 403 if header is absent, so we set
# auto_error=False and handle 401 ourselves for a consistent error contract.
_bearer = HTTPBearer(auto_error=False)


# ── Token creation ─────────────────────────────────────────────────────────────
def create_access_token(user_id: str, role: str) -> str:
    """
    Create a signed JWT containing ``user_id`` and ``role``.
    The token expires after ACCESS_TOKEN_EXPIRE_HOURS hours.
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ── Base dependency ────────────────────────────────────────────────────────────
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> dict:
    """
    Decode the Bearer token from the Authorization header.

    Returns a dict ``{"user_id": str, "role": str}``.

    Raises:
        HTTP 401 – if the token is missing, expired, or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        if user_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Role-specific dependencies ─────────────────────────────────────────────────
async def get_current_farmer(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Extends ``get_current_user`` by enforcing role == "farmer".

    Raises:
        HTTP 403 – if the authenticated user is not a farmer.
    """
    if current_user["role"] != "farmer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to farmers",
        )
    return current_user


async def get_current_buyer(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Extends ``get_current_user`` by enforcing role == "buyer".

    Raises:
        HTTP 403 – if the authenticated user is not a buyer.
    """
    if current_user["role"] != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to buyers",
        )
    return current_user
