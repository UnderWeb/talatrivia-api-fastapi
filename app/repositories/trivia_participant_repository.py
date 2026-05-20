# app/repositories/trivia_participant_repository.py
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models.enums import TriviaParticipantStatus
from app.models.trivia_participant import TriviaParticipant
from app.models.user import User


class TriviaParticipantRepository:
    """
    Repository for trivia participant operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_user_and_trivia(
        self, user_id: int, trivia_id: int
    ) -> TriviaParticipant | None:
        """
        Retrieve a participant by user and trivia identifiers.
        """
        stmt = select(TriviaParticipant).where(
            TriviaParticipant.user_id == user_id,
            TriviaParticipant.trivia_id == trivia_id,
        )

        return self.db.execute(stmt).scalar_one_or_none()

    def get_ranking(self, trivia_id: int) -> list[TriviaParticipant]:
        """
        Retrieve completed participants ordered by ranking score.

        Final tie-break ordering is completed in the service layer
        to ensure database portability across SQLite/PostgreSQL.
        """
        stmt = (
            select(TriviaParticipant)
            .join(User, TriviaParticipant.user_id == User.id)
            .where(
                TriviaParticipant.trivia_id == trivia_id,
                TriviaParticipant.status == TriviaParticipantStatus.COMPLETED,
            )
            .order_by(
                desc(TriviaParticipant.score),
                asc(TriviaParticipant.id),
            )
        )

        return list(self.db.execute(stmt).scalars().all())
