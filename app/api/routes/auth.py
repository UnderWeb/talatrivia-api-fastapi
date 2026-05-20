# app/api/routes/auth.py
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.mappers.user_mapper import UserMapper
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
)
from app.schemas.user import UserOut, UserRegister
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """
    Dependency provider for AuthService.
    """
    return AuthService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Dependency provider for UserService.
    """
    return UserService(db)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Authenticate user and return access token.
    """
    access_token, refresh_token, user = service.login(payload.email, payload.password)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserMapper.to_out(user),
    )


@router.post(
    "/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK
)
def refresh_token(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> RefreshTokenResponse:
    """
    Generate new access token using refresh token.
    """
    access_token = service.refresh_access_token(payload.refresh_token)

    return RefreshTokenResponse(access_token=access_token)


@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def me(user: User = Depends(get_current_user)) -> UserOut:
    """
    Return current authenticated user profile.
    """
    return UserMapper.to_out(user)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegister,
    service: UserService = Depends(get_user_service),
) -> UserOut:
    """
    Public player registration endpoint.

    All users created through this endpoint are assigned PLAYER role automatically.
    """
    user = service.create_player(
        name=payload.name,
        email=payload.email,
        password=payload.password,
    )

    return UserMapper.to_out(user)
