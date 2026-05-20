# app/mappers/user_mapper.py
from app.models.user import User
from app.schemas.user import UserOut


class UserMapper:
    """
    Maps User ORM entities to Pydantic schemas.
    """

    @staticmethod
    def to_out(user: User) -> UserOut:
        """
        Map user entity to response schema.
        """
        return UserOut(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
        )

    @staticmethod
    def to_out_list(users: list[User]) -> list[UserOut]:
        """
        Map user list to response schema list.
        """
        return [UserMapper.to_out(user) for user in users]
