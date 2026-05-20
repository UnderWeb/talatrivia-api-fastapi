# tests/services/test_question_service.py
from app.models.enums import DifficultyLevel
from app.schemas.question import QuestionOptionCreate
from app.services.question_service import QuestionService


def test_question_service_create_question(db_session):
    """
    QuestionService.create_question

    Requirement:
    Questions must be created with exactly one correct option and valid unique options.

    Expectation:
    Returns persisted question with options correctly stored.
    """
    service = QuestionService(db_session)

    question = service.create_question(
        text="What is 2+2?",
        difficulty=DifficultyLevel.EASY,
        options=[
            QuestionOptionCreate(
                text="4",
                is_correct=True,
            ),
            QuestionOptionCreate(
                text="5",
                is_correct=False,
            ),
        ],
    )

    assert question.id is not None
    assert question.text == "What is 2+2?"
    assert len(question.options) == 2
    assert any(opt.is_correct for opt in question.options)
