# tests/services/test_ranking_service.py
from datetime import datetime, timedelta, timezone

from app.models.enums import (
    DifficultyLevel,
    TriviaParticipantStatus,
    UserRole,
)
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.trivia import Trivia
from app.models.trivia_participant import TriviaParticipant
from app.models.trivia_question import TriviaQuestion
from app.models.user import User
from app.services.ranking_service import RankingService


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


def test_ranking_sorted(db_session, admin_user):
    """
    RankingService.get_trivia_ranking

    Requirement:
    Ranking must be ordered by descending score.

    Expectation:
    Higher score appears first.
    """
    question = create_question(db_session, "Ranking Question")

    trivia = Trivia(name="Ranking Trivia", description="Ranking validation")

    db_session.add(trivia)
    db_session.commit()
    db_session.refresh(trivia)

    trivia_question = TriviaQuestion(
        trivia_id=trivia.id,
        question_id=question.id,
        position=1,
    )

    second_user = User(
        name="Second User",
        email="second@test.com",
        hashed_password="fake-hash",
        role=UserRole.PLAYER,
    )

    db_session.add(second_user)
    db_session.commit()
    db_session.refresh(second_user)

    now = datetime.now(timezone.utc)

    participant_high = TriviaParticipant(
        user_id=admin_user.id,
        trivia_id=trivia.id,
        status=TriviaParticipantStatus.COMPLETED,
        score=100,
        started_at=now,
        finished_at=now + timedelta(minutes=5),
    )

    participant_low = TriviaParticipant(
        user_id=second_user.id,
        trivia_id=trivia.id,
        status=TriviaParticipantStatus.COMPLETED,
        score=50,
        started_at=now,
        finished_at=now + timedelta(minutes=7),
    )

    db_session.add_all(
        [
            trivia_question,
            participant_high,
            participant_low,
        ]
    )

    db_session.commit()

    service = RankingService(db_session)
    result = service.get_trivia_ranking(trivia.id)

    assert len(result.ranking) == 2

    scores = [entry.score for entry in result.ranking]

    assert scores == [100, 50]
