# app/services/auth_service.py
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository

from .base_service import BaseService


class AuthService(BaseService):
    """
    Stateless JWT authentication service.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.user_repo = UserRepository(db)

    def login(self, email: str, password: str) -> tuple[str, str, User]:
        """
        Authenticate credentials and issue JWT token.
        """
        user = self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid credentials.")

        payload = {
            "sub": str(user.id),
            "role": user.role.value,
        }

        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)

        self.logger.info(
            "User authenticated successfully: user_id=%s",
            user.id,
        )

        return access_token, refresh_token, user

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        """
        payload = verify_token(refresh_token, expected_type="refresh")
        user = self.user_repo.get_by_id(int(payload["sub"]))

        if not user:
            raise UnauthorizedException("User not found")

        return create_access_token(
            {
                "sub": str(user.id),
                "role": user.role.value,
            }
        )

    def get_current_user(self, user_id: int) -> User:
        """
        Retrieve authenticated user profile.
        """
        user = self.user_repo.get_by_id(user_id)

        if not user:
            self.logger.warning(
                "Authenticated user not found user_id=%s",
                user_id,
            )
            raise UnauthorizedException("User not found")

        return user
