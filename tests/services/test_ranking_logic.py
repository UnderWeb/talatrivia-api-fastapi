# tests/services/test_ranking_logic.py
from datetime import datetime, timedelta, timezone

from app.models.enums import TriviaParticipantStatus, UserRole
from app.models.trivia import Trivia
from app.models.trivia_participant import TriviaParticipant
from app.models.user import User
from app.services.ranking_service import RankingService


def test_ranking_time_tie_break(db_session, admin_user):
    """
    RankingService.get_trivia_ranking

    Requirement:
    Same-score participants must be ordered
    by fastest completion time.

    Expectation:
    Faster participant appears first.
    """
    trivia = Trivia(name="Time Challenge", description="Tie-break validation trivia")

    db_session.add(trivia)
    db_session.commit()
    db_session.refresh(trivia)

    slow_user = User(
        name="Slow Player",
        email="slow.player@test.com",
        hashed_password="fake-hash",
        role=UserRole.PLAYER,
    )

    db_session.add(slow_user)
    db_session.commit()
    db_session.refresh(slow_user)

    base_time = datetime.now(timezone.utc)

    fast_participant = TriviaParticipant(
        user_id=admin_user.id,
        trivia_id=trivia.id,
        status=TriviaParticipantStatus.COMPLETED,
        score=100,
        started_at=base_time,
        finished_at=base_time + timedelta(minutes=5),
    )

    slow_participant = TriviaParticipant(
        user_id=slow_user.id,
        trivia_id=trivia.id,
        status=TriviaParticipantStatus.COMPLETED,
        score=100,
        started_at=base_time,
        finished_at=base_time + timedelta(minutes=10),
    )

    db_session.add_all([fast_participant, slow_participant])
    db_session.commit()

    service = RankingService(db_session)
    result = service.get_trivia_ranking(trivia.id)
    ranking = result.ranking

    assert len(ranking) == 2

    assert ranking[0].user_id == admin_user.id
    assert ranking[0].score == 100
    assert ranking[0].total_time_seconds == 300

    assert ranking[1].user_id == slow_user.id
    assert ranking[1].score == 100
    assert ranking[1].total_time_seconds == 600
