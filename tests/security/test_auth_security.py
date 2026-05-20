# tests/security/test_auth_security.py
from fastapi import status


def test_invalid_token_format_rejected(client):
    """
    Authentication Security Contract

    Requirement:
    All protected endpoints must reject malformed JWT tokens.

    Expectation:
    System must return 401 Unauthorized without leaking internal errors.
    """
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    data = response.json()

    assert "detail" in data
    assert data["detail"] is not None


def test_valid_token_allows_access(client, auth_header_admin):
    """
    Requirement:
    Valid JWT must grant access to protected endpoints.

    Expectation:
    200 OK for authenticated requests.
    """
    response = client.get("/api/v1/users", headers=auth_header_admin)

    assert response.status_code == 200


def test_missing_token_returns_401(client):
    """
    Requirement:
    Missing Authorization header must be rejected.

    Expectation:
    401 Unauthorized.
    """
    response = client.get("/api/v1/users")

    assert response.status_code == 401


def test_empty_bearer_token(client):
    """
    Authentication Security Contract

    Requirement:
    Authorization header must include a valid Bearer token.

    Expectation:
    Requests with empty Bearer token must be rejected with 401 Unauthorized.
    """
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": "Bearer"},
    )

    assert response.status_code == 401
