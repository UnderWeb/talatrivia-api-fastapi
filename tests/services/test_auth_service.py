# tests/services/test_auth_service.py
import pytest

from app.core.exceptions import UnauthorizedException
from app.core.security import hash_password
from app.models.user import User
from app.services.auth_service import AuthService


def test_auth_service_login_success(db_session):
    """
    AuthService.login

    Requirement:
    Valid credentials must return JWT tokens.

    Expectation:
    Access token and refresh token are returned.
    """
    user = User(
        name="Auth User",
        email="auth@test.com",
        hashed_password=hash_password("password123"),
    )

    db_session.add(user)
    db_session.commit()

    service = AuthService(db_session)

    access_token, refresh_token, user_obj = service.login(
        "auth@test.com",
        "password123",
    )

    assert isinstance(access_token, str)
    assert len(access_token) > 10

    assert isinstance(refresh_token, str)
    assert len(refresh_token) > 10

    assert isinstance(user_obj, User)


def test_auth_service_login_invalid_email(db_session):
    """
    AuthService.login

    Requirement:
    Invalid email must be rejected.

    Expectation:
    Raises UnauthorizedException.
    """
    service = AuthService(db_session)

    with pytest.raises(UnauthorizedException):
        service.login("missing@test.com", "password")


def test_auth_service_login_invalid_password(db_session):
    """
    AuthService.login

    Requirement:
    Wrong password must be rejected.

    Expectation:
    Raises UnauthorizedException.
    """
    user = User(
        name="Auth User",
        email="auth2@test.com",
        hashed_password=hash_password("correct"),
    )

    db_session.add(user)
    db_session.commit()

    service = AuthService(db_session)

    with pytest.raises(UnauthorizedException):
        service.login("auth2@test.com", "wrong")
