# tests/repositories/test_answer_repository.py
from app.models.answer import Answer
from app.models.enums import DifficultyLevel
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.trivia import Trivia
from app.models.user import User
from app.repositories.answer_repository import AnswerRepository


def test_answer_repository_create_and_get(db_session):
    """
    AnswerRepository.create + get_by_id

    Requirement:
    Answers must persist correctly.

    Expectation:
    Persisted answer is retrievable by ID.
    """
    user = User(
        name="Answer User",
        email="answer.repo@test.com",
        hashed_password="fake-hash",
    )

    question = Question(
        text="Repository Question",
        difficulty=DifficultyLevel.EASY,
        options=[
            QuestionOption(
                text="Correct",
                is_correct=True,
            ),
            QuestionOption(
                text="Wrong",
                is_correct=False,
            ),
        ],
    )

    trivia = Trivia(
        name="Repository Trivia",
        description="Repository validation",
    )

    db_session.add_all(
        [
            user,
            question,
            trivia,
        ]
    )

    db_session.commit()

    option = question.options[0]
    repo = AnswerRepository(db_session)

    answer = Answer(
        user_id=user.id,
        trivia_id=trivia.id,
        question_id=question.id,
        selected_option_id=option.id,
        points_awarded=10,
    )

    created = repo.create(answer)

    db_session.commit()

    fetched = repo.get_by_id(created.id)

    assert fetched is not None

    assert fetched.user_id == user.id
    assert fetched.trivia_id == trivia.id
    assert fetched.question_id == question.id
    assert fetched.points_awarded == 10
