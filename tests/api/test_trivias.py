# tests/api/test_trivias.py
from fastapi import status


def create_question(client, auth_header_admin, text: str) -> int:
    response = client.post(
        "/api/v1/questions",
        json={
            "text": text,
            "difficulty": "easy",
            "options": [
                {
                    "text": "Correct",
                    "is_correct": True,
                },
                {
                    "text": "Incorrect",
                    "is_correct": False,
                },
            ],
        },
        headers=auth_header_admin,
    )

    assert response.status_code == status.HTTP_201_CREATED

    return response.json()["id"]


def test_create_trivia_success(client, auth_header_admin, admin_user):
    """
    Trivia creation

    Requirement:
    Admins must be able to create trivias
    with questions and participants.

    Expectation:
    201 Created with linked questions.
    """
    question_id = create_question(client, auth_header_admin, "What is 2+2?")

    payload = {
        "name": "Math Challenge",
        "description": "Basic arithmetic",
        "question_ids": [question_id],
    }

    response = client.post(
        "/api/v1/trivias",
        json=payload,
        headers=auth_header_admin,
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["name"] == payload["name"]

    assert len(data["questions"]) == 1
    assert data["questions"][0]["id"] == question_id


def test_create_trivia_duplicate_questions_fails(client, auth_header_admin, admin_user):
    """
    Trivia creation validation

    Requirement:
    Duplicate question IDs are invalid.

    Expectation:
    422 validation error.
    """
    question_id = create_question(client, auth_header_admin, "Duplicate validation")

    payload = {
        "name": "Invalid Trivia",
        "description": "Testing duplicates",
        "question_ids": [question_id, question_id],
    }

    response = client.post("/api/v1/trivias", json=payload, headers=auth_header_admin)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_ranking_empty_trivia_success(client, auth_header_admin, admin_user):
    """
    Trivia ranking

    Requirement:
    Empty rankings must return valid response structure.

    Expectation:
    200 OK with empty ranking list.
    """
    question_id = create_question(client, auth_header_admin, "Ranking Test Question")

    trivia_response = client.post(
        "/api/v1/trivias",
        json={
            "name": "Empty Ranking Trivia",
            "description": None,
            "question_ids": [question_id],
        },
        headers=auth_header_admin,
    )

    assert trivia_response.status_code == status.HTTP_201_CREATED

    trivia_id = trivia_response.json()["id"]

    response = client.get(
        f"/api/v1/trivias/{trivia_id}/ranking",
        headers=auth_header_admin,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["trivia_id"] == trivia_id
    assert isinstance(data["ranking"], list)
    assert len(data["ranking"]) == 0
