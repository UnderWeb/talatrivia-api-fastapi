# tests/services/test_trivia_service.py
import pytest

from app.core.exceptions import BadRequestException
from app.models.enums import DifficultyLevel
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.services.trivia_service import TriviaService


def create_question(db_session, text: str) -> Question:
    question = Question(
        text=text,
        difficulty=DifficultyLevel.EASY,
        options=[
            QuestionOption(
                text="Correct",
                is_correct=True,
            ),
            QuestionOption(
                text="Incorrect",
                is_correct=False,
            ),
        ],
    )

    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)

    return question


def test_trivia_service_create_success(db_session):
    """
    TriviaService.create_trivia

    Requirement:
    A trivia must be created with questions and participants.

    Expectation:
    Returns persisted trivia entity with linked relations.
    """
    question = create_question(db_session, "What is SOLID?")
    service = TriviaService(db_session)

    trivia = service.create_trivia(
        name="Trivia Test",
        description="Architecture trivia",
        question_ids=[question.id],
    )

    assert trivia.id is not None
    assert trivia.name == "Trivia Test"

    assert len(trivia.questions) == 1

    trivia_question = trivia.questions[0]

    assert trivia_question.question_id == question.id
    assert trivia_question.position == 1


def test_trivia_service_duplicate_questions_fails(db_session):
    """
    TriviaService.create_trivia

    Requirement:
    Duplicate question IDs are not allowed.

    Expectation:
    Raises BadRequestException.
    """
    question = create_question(db_session, "Duplicate question validation")
    service = TriviaService(db_session)

    with pytest.raises(BadRequestException):
        service.create_trivia(
            name="Invalid Trivia",
            description="Testing duplicates",
            question_ids=[question.id, question.id],
        )
