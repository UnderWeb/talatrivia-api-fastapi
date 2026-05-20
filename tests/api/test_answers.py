# tests/api/test_answers.py
from fastapi import status


def create_question(client, auth_header_admin):
    response = client.post(
        "/api/v1/questions",
        json={
            "text": "What is the capital of France?",
            "difficulty": "easy",
            "options": [
                {
                    "text": "Paris",
                    "is_correct": True,
                },
                {
                    "text": "Lyon",
                    "is_correct": False,
                },
            ],
        },
        headers=auth_header_admin,
    )

    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


def create_trivia(client, auth_header_admin, question_id: int):
    response = client.post(
        "/api/v1/trivias",
        json={
            "name": "Geography Trivia",
            "description": "World geography",
            "question_ids": [question_id],
        },
        headers=auth_header_admin,
    )

    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


def join_trivia(client, auth_header_player, trivia_id: int):
    response = client.post(
        f"/api/v1/trivias/{trivia_id}/join",
        headers=auth_header_player,
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_submit_answer_flow(client, auth_header_admin, auth_header_player):
    """
    Answer API Flow

    Requirement:
    A participant must be able to:
    create question → create trivia → join trivia → submit answer.

    Expectation:
    Returns 201 Created with a persisted Answer
    linked to trivia and question, including awarded points.
    """
    question = create_question(client, auth_header_admin)
    trivia = create_trivia(client, auth_header_admin, question["id"])

    join_trivia(client, auth_header_player, trivia["id"])

    correct_option_id = next(
        option["id"] for option in question["options"] if option["is_correct"]
    )

    response = client.post(
        "/api/v1/answers",
        json={
            "trivia_id": trivia["id"],
            "question_id": question["id"],
            "selected_option_id": correct_option_id,
        },
        headers=auth_header_player,
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_submit_duplicate_answer_fails(client, auth_header_admin, auth_header_player):
    """
    Answer API Duplicate Prevention

    Requirement:
    A user cannot submit the same answer twice for the same question in a trivia.

    Expectation:
    Second submission must return 409 CONFLICT.
    """
    question = create_question(client, auth_header_admin)
    trivia = create_trivia(client, auth_header_admin, question["id"])

    join_trivia(client, auth_header_player, trivia["id"])

    correct_option_id = next(
        option["id"] for option in question["options"] if option["is_correct"] is True
    )

    payload = {
        "trivia_id": trivia["id"],
        "question_id": question["id"],
        "selected_option_id": correct_option_id,
    }

    first = client.post("/api/v1/answers", json=payload, headers=auth_header_player)
    assert first.status_code == status.HTTP_201_CREATED

    second = client.post("/api/v1/answers", json=payload, headers=auth_header_player)
    assert second.status_code == status.HTTP_409_CONFLICT
