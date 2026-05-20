# tests/repositories/test_question_repository.py
from app.models.enums import DifficultyLevel
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.repositories.question_repository import QuestionRepository


def test_question_repository_create_and_get(db_session):
    """
    QuestionRepository.create + get_by_id

    Requirement:
    Questions must be persisted with their options.

    Expectation:
    Retrieved question must include its options.
    """
    repo = QuestionRepository(db_session)

    question = Question(
        text="What is 2+2?",
        difficulty=DifficultyLevel.EASY,
        options=[
            QuestionOption(text="4", is_correct=True),
            QuestionOption(text="5", is_correct=False),
        ],
    )

    created = repo.create(question)
    db_session.commit()

    fetched = repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.text == "What is 2+2?"
    assert len(fetched.options) == 2
