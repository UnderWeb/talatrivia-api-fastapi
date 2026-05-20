# app/repositories/user_repository.py
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Repository for user persistence operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        """
        Persist a new user entity.
        """
        self.db.add(user)
        self.db.flush()

        return user

    def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve user by identifier.
        """
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """
        Retrieve user by normalized email.
        """
        stmt = select(User).where(User.email == email)

        return self.db.execute(stmt).scalar_one_or_none()

    def exists_by_email(self, email: str) -> bool:
        """
        Check whether a user email already exists.
        """
        stmt = select(exists().where(User.email == email))

        return bool(self.db.execute(stmt).scalar_one())

    def get_all(self) -> list[User]:
        """
        Retrieve all users ordered by identifier.
        """
        stmt = select(User).order_by(User.id)

        return list(self.db.execute(stmt).scalars().all())
