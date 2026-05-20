# tests/api/test_questions.py
from fastapi import status

from app.models.enums import DifficultyLevel


def test_create_question_as_admin_success(client, auth_header_admin):
    """
    Question creation

    Requirement:
    Admins must be able to create new questions
    with multiple options.

    Expectation:
    201 Created with question and generated option IDs.
    """
    payload = {
        "text": "What does the 'S' in SOLID stand for?",
        "difficulty": DifficultyLevel.MEDIUM,
        "options": [
            {"text": "Single Responsibility", "is_correct": True},
            {"text": "Simple Logic", "is_correct": False},
        ],
    }

    response = client.post("/api/v1/questions", json=payload, headers=auth_header_admin)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()

    assert data["text"] == payload["text"]
    assert "id" in data

    assert len(data["options"]) == 2

    for option in data["options"]:
        assert "id" in option
        assert "text" in option


def test_list_questions_public_access(client, auth_header_admin):
    """
    Question listing

    Requirement:
    Users must be able to retrieve questions
    without seeing correct answers.

    Expectation:
    200 OK and list of questions without is_correct field.
    """
    created = client.post(
        "/api/v1/questions",
        json={
            "text": "Sample Q",
            "difficulty": DifficultyLevel.EASY,
            "options": [
                {"text": "A", "is_correct": True},
                {"text": "B", "is_correct": False},
            ],
        },
        headers=auth_header_admin,
    ).json()

    response = client.get("/api/v1/questions", headers=auth_header_admin)

    assert response.status_code == status.HTTP_200_OK

    questions = response.json()

    assert isinstance(questions, list)

    question = next(q for q in questions if q["id"] == created["id"])

    assert question["text"] == "Sample Q"

    assert len(question["options"]) == 2

    for option in question["options"]:
        assert "id" in option
        assert "text" in option
        assert "is_correct" not in option
