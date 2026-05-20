# app/services/user_service.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ResourceNotFoundException
from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository

from .base_service import BaseService


class UserService(BaseService):
    """
    User management service.

    Separates public self-registration flows from
    administrative user management workflows.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.user_repo = UserRepository(db)

    def create_player(self, name: str, email: str, password: str) -> User:
        """
        Public self-registration flow.

        Always creates PLAYER users.
        """
        return self._create_user(
            name=name,
            email=email,
            password=password,
            role=UserRole.PLAYER,
        )

    def create_admin_user(
        self, name: str, email: str, password: str, role: UserRole
    ) -> User:
        """
        Administrative user creation flow.

        Allows admins to create users with explicit roles.
        """
        return self._create_user(
            name=name,
            email=email,
            password=password,
            role=role,
        )

    def _create_user(
        self, name: str, email: str, password: str, role: UserRole
    ) -> User:
        """
        Internal user creation implementation.
        """

        try:
            user = User(
                name=name,
                email=email,
                hashed_password=hash_password(password),
                role=role,
            )

            created_user = self.user_repo.create(user)
            self.commit()

            self.logger.info(
                "User created successfully user_id=%s role=%s",
                created_user.id,
                created_user.role.value,
            )

            return created_user
        except IntegrityError as exc:
            self.rollback()
            raise ConflictException("Email already registered.") from exc
        except Exception:
            self.rollback()
            raise

    def get_by_id(self, user_id: int) -> User:
        """
        Retrieve user by ID.
        """
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise ResourceNotFoundException("User not found.")

        return user

    def get_by_email(self, email: str) -> User:
        """
        Retrieve user by email.
        """
        user = self.user_repo.get_by_email(email)

        if not user:
            raise ResourceNotFoundException("User not found.")

        return user

    def get_all(self) -> list[User]:
        """
        Retrieve all users.
        """
        return self.user_repo.get_all()
