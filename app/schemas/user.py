# app/schemas/user.py
from pydantic import EmailStr, Field, field_validator

from app.models.enums import UserRole

from .common import BaseSchema


class UserRegister(BaseSchema):
    """
    Public player registration schema.
    """

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr = Field(max_length=150)
    password: str = Field(min_length=8, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.strip().lower()


class UserCreateAdmin(UserRegister):
    """
    Administrative user creation schema.
    """

    role: UserRole = UserRole.PLAYER


class UserOut(BaseSchema):
    """
    Public user representation.
    """

    id: int
    name: str
    email: EmailStr
    role: UserRole
