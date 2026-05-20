# app/api/routes/users.py
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_admin
from app.api.dependencies.database import get_db
from app.mappers.user_mapper import UserMapper
from app.models.user import User
from app.schemas.user import UserCreateAdmin, UserOut
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Dependency provider for UserService.
    """
    return UserService(db)


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreateAdmin,
    _: User = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> UserOut:
    """
    Create a new user.

    Restricted to admin users.
    """
    user = service.create_admin_user(
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )

    return UserMapper.to_out(user)


@router.get("/", response_model=list[UserOut], status_code=status.HTTP_200_OK)
def list_users(
    _: User = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> list[UserOut]:
    """
    List registered users.

    Restricted to admin users.
    """
    users = service.get_all()

    return UserMapper.to_out_list(users)


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user(
    user_id: int,
    _: User = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> UserOut:
    """
    Retrieve a specific user by identifier.
    """
    user = service.get_by_id(user_id)
    return UserMapper.to_out(user)
