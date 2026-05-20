# tests/api/test_auth.py
from fastapi import status

from app.core.security import hash_password
from app.models.user import User


def test_login_user_success(client, db_session):
    """
    Auth login

    Requirement:
    User must receive JWT + user info.

    Expectation:
    200 OK with access_token, token_type and user object.
    """
    user = User(
        name="Login User",
        email="auth_test@example.com",
        hashed_password=hash_password("password123"),
    )

    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "auth_test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "auth_test@example.com"


def test_get_me_success(client, auth_header_admin, admin_user):
    """
    Auth me endpoint

    Requirement:
    The system must return the currently authenticated user.

    Expectation:
    200 OK with the user profile corresponding
    to the JWT identity.
    """
    response = client.get("/api/v1/auth/me", headers=auth_header_admin)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == admin_user.id
    assert data["email"] == admin_user.email
    assert data["name"] == admin_user.name

    # Security check
    assert "hashed_password" not in data
