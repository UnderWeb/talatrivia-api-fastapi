# tests/services/test_user_service.py
import uuid

import pytest

from app.core.exceptions import ConflictException, ResourceNotFoundException
from app.models.enums import UserRole
from app.services.user_service import UserService


def unique_email() -> str:
    return f"{uuid.uuid4()}@test.com"


def test_create_player_success(db_session):
    """
    UserService.create_player

    Requirement:
    A player must be created with a unique email.

    Expectation:
    Returns persisted player with normalized email.
    """
    service = UserService(db_session)

    user = service.create_player(
        name="Player",
        email="player@test.com",
        password="password123",
    )

    assert user.id is not None
    assert user.role == UserRole.PLAYER


def test_create_admin_user_success(db_session):
    """
    UserService.create_admin_user

    Requirement:
    An admin user must be creatable with a specified role.

    Expectation:
    Returns persisted admin user with correct role.
    """
    service = UserService(db_session)

    user = service.create_admin_user(
        name="Admin",
        email="admin@test.com",
        password="password123",
        role=UserRole.ADMIN,
    )

    assert user.role == UserRole.ADMIN


def test_duplicate_email_fails(db_session):
    """
    UserService.create_player

    Requirement:
    Email must be unique across players.

    Expectation:
    Raises ConflictException on duplicate email.
    """
    service = UserService(db_session)
    service.create_player(name="User1", email="dup@test.com", password="password123")

    with pytest.raises(ConflictException):
        service.create_player(
            name="User2",
            email="dup@test.com",
            password="password123",
        )


def test_get_by_id_success(db_session):
    """
    UserService.get_user

    Requirement:
    Must retrieve user by ID.

    Expectation:
    Returns correct user entity.
    """
    service = UserService(db_session)
    created = service.create_player(
        name="Find Me",
        email=unique_email(),
        password="password123",
    )

    result = service.get_by_id(created.id)

    assert result.id == created.id


def test_get_by_id_not_found(db_session):
    """
    UserService.get_user

    Requirement:
    Non-existent user must raise error.

    Expectation:
    ResourceNotFoundException is raised.
    """
    service = UserService(db_session)

    with pytest.raises(ResourceNotFoundException):
        service.get_by_id(99999)


def test_get_all_users(db_session):
    """
    UserService.get_all

    Requirement:
    Must retrieve all users.

    Expectation:
    Returns list of all user entities.
    """
    service = UserService(db_session)

    service.create_player(
        name="User A",
        email="a@test.com",
        password="password123",
    )

    service.create_player(
        name="User B",
        email="b@test.com",
        password="password123",
    )

    users = service.get_all()

    assert len(users) >= 2
