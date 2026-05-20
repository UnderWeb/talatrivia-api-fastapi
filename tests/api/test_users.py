# tests/api/test_users.py
from fastapi import status

from app.core.security import create_access_token
from app.models.enums import UserRole
from app.models.user import User


def test_list_users_as_admin_success(client, auth_header_admin):
    """
    UserService.list_users

    Requirement:
    Admin users must be able to retrieve all users.

    Expectation:
    200 OK with list of users excluding sensitive fields.
    """
    response = client.get("/api/v1/users", headers=auth_header_admin)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_user = data[0]

    assert "id" in first_user
    assert "name" in first_user
    assert "email" in first_user
    assert "role" in first_user

    assert "hashed_password" not in first_user
    assert "password" not in first_user


def test_list_users_unauthorized_fails(client):
    """
    require_admin dependency

    Requirement:
    Requests without authentication must be rejected.

    Expectation:
    401 Unauthorized.
    """
    response = client.get("/api/v1/users")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    data = response.json()

    assert data["detail"] == "Not authenticated"


def test_list_users_as_player_forbidden(client, db_session):
    """
    require_admin dependency

    Requirement:
    Authenticated users without ADMIN role must be forbidden.

    Expectation:
    403 Forbidden.
    """

    player = User(
        name="Player",
        email="player@test.com",
        hashed_password="fake",
        role=UserRole.PLAYER,
    )

    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)

    player_token = create_access_token(
        {
            "sub": str(player.id),
            "role": player.role.value,
        }
    )

    headers = {
        "Authorization": f"Bearer {player_token}",
    }

    response = client.get(
        "/api/v1/users",
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    data = response.json()

    assert data["detail"] == "You do not have the necessary permissions"


def test_get_user_by_id_success(client, auth_header_admin, db_session):
    """
    UserService.get_by_id

    Requirement:
    Must retrieve user by ID.

    Expectation:
    Returns correct user entity.
    """
    user = User(
        name="Find",
        email="find@test.com",
        hashed_password="x",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.get(f"/api/v1/users/{user.id}", headers=auth_header_admin)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == user.id
    assert data["email"] == "find@test.com"


def test_get_user_by_id_not_found(client, auth_header_admin):
    """
    UserService.get_by_id

    Requirement:
    Non-existent user must raise error.

    Expectation:
    404 Not Found.
    """
    response = client.get("/api/v1/users/99999", headers=auth_header_admin)

    assert response.status_code == status.HTTP_404_NOT_FOUND
