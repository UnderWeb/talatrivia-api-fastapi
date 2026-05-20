# app/schemas/auth.py
from pydantic import EmailStr, Field, field_validator

from app.models.enums import UserRole

from .common import BaseSchema
from .user import UserOut


class LoginRequest(BaseSchema):
    """
    Authentication request payload.
    """

    email: EmailStr = Field(max_length=150)
    password: str = Field(min_length=8, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return value.strip().lower()


class RefreshTokenRequest(BaseSchema):
    """
    Refresh token request payload.
    """

    refresh_token: str


class TokenResponse(BaseSchema):
    """
    JWT authentication response.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class RefreshTokenResponse(BaseSchema):
    """
    Refresh access token response.
    """

    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseSchema):
    """
    Authenticated user profile response.
    """

    id: int
    name: str
    email: EmailStr
    role: UserRole
