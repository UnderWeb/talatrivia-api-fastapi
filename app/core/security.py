# app/core/security.py
"""Security utilities for JWT authentication and password hashing."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.logger import get_logger

logger = get_logger("security")


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validate password against hashed value."""
    return pwd_context.verify(plain_password, hashed_password)


def _build_token(
    *,
    data: dict[str, Any],
    expires_delta: timedelta,
    token_type: str,
) -> str:
    """
    Internal JWT builder.
    """
    user_id = data.get("sub")
    role = data.get("role")

    if not user_id or not role:
        raise ValueError("Token payload requires 'sub' and 'role'")

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": str(user_id),
        "role": str(role),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(data: dict[str, Any]) -> str:
    """
    Generate JWT access token.
    """
    logger.info(
        "Creating access token for user_id=%s",
        data.get("sub"),
    )

    return _build_token(
        data=data,
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
        token_type="access",
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Generate JWT refresh token.
    """
    logger.info(
        "Creating refresh token for user_id=%s",
        data.get("sub"),
    )

    return _build_token(
        data=data,
        expires_delta=timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        ),
        token_type="refresh",
    )


def verify_token(
    token: str,
    expected_type: str | None = None,
) -> dict[str, Any]:
    """
    Decode and validate JWT token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        sub = payload.get("sub")
        role = payload.get("role")
        token_type = payload.get("type")
        iat = payload.get("iat")
        exp = payload.get("exp")

        if (
            sub is None
            or role is None
            or token_type is None
            or iat is None
            or exp is None
        ):
            raise UnauthorizedException("Invalid token payload")

        if expected_type and token_type != expected_type:
            raise UnauthorizedException("Invalid token type")

        return {
            "sub": str(sub),
            "role": str(role),
            "type": str(token_type),
            "iat": int(iat),
            "exp": int(exp),
        }

    except ExpiredSignatureError as exc:
        logger.warning("Expired JWT token")
        raise UnauthorizedException("Token has expired") from exc

    except JWTError as exc:
        logger.warning("Invalid JWT token")
        raise UnauthorizedException("Invalid token") from exc


def get_current_user_id_from_token(token: str) -> int:
    """
    Extract authenticated user id from JWT token.
    """
    payload = verify_token(
        token,
        expected_type="access",
    )

    try:
        return int(payload["sub"])

    except (TypeError, ValueError) as exc:
        raise UnauthorizedException("Invalid token subject") from exc
