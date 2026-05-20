# tests/api/test_error_handlers.py
from fastapi import status


def test_resource_not_found_handler_on_trivia_ranking(client, auth_header_admin):
    """
    Error Handling

    Requirement:
    The system must return a consistent error response
    when requesting a non-existent resource.

    Expectation:
    404 NOT FOUND with standardized error code.
    """
    response = client.get(
        "/api/v1/trivias/9999/ranking",
        headers=auth_header_admin,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    data = response.json()

    assert "detail" in data
