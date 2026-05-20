# app/api/dependencies/auth.py
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.core.logger import get_logger
from app.core.security import verify_token
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = get_logger(__name__)

bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
)


def _unauthorized_exception(
    detail: str = "Could not validate credentials",
) -> HTTPException:
    """
    Standardized authentication exception response.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve and validate the authenticated user from JWT token.
    """
    try:
        payload = verify_token(credentials.credentials)
    except Exception:
        logger.warning(
            "JWT validation failed",
        )
        raise _unauthorized_exception(
            "Invalid or expired token",
        )

    user_id = payload.get("sub")

    if not user_id:
        logger.warning(
            "Token payload missing subject claim",
        )
        raise _unauthorized_exception()

    try:
        user_id_int = int(user_id)

    except (TypeError, ValueError):
        logger.warning(
            "Invalid token subject format subject=%s",
            user_id,
        )
        raise _unauthorized_exception(
            "Invalid authentication token",
        )

    user_repo = UserRepository(db)

    user = user_repo.get_by_id(user_id_int)

    if not user:
        logger.warning(
            "Authenticated user no longer exists user_id=%s",
            user_id_int,
        )
        raise _unauthorized_exception(
            "User no longer exists",
        )

    return user


def require_role(
    role: UserRole,
) -> Callable[[User], User]:
    """
    Factory dependency for RBAC validation.
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role != role:
            logger.warning(
                ("Access denied for user_id=%s required_role=%s actual_role=%s"),
                current_user.id,
                role.value,
                current_user.role.value,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the necessary permissions",
            )

        return current_user

    return role_checker


require_admin = require_role(UserRole.ADMIN)
