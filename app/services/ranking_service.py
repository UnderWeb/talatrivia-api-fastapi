# app/services/ranking_service.py
from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundException
from app.models.trivia_participant import TriviaParticipant
from app.repositories.trivia_participant_repository import (
    TriviaParticipantRepository,
)
from app.repositories.trivia_repository import TriviaRepository
from app.schemas.ranking import RankingItem, RankingResponse

from .base_service import BaseService


class RankingService(BaseService):
    """
    Trivia ranking service.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.participant_repo = TriviaParticipantRepository(db)
        self.trivia_repo = TriviaRepository(db)

    @staticmethod
    def _get_completion_time_seconds(participant: TriviaParticipant) -> int:
        """
        Calculate participant completion time in seconds.

        Incomplete timing data is ranked last.
        """
        if participant.started_at is None or participant.finished_at is None:
            return 10**12

        return int((participant.finished_at - participant.started_at).total_seconds())

    def get_trivia_ranking(self, trivia_id: int) -> RankingResponse:
        """
        Retrieve trivia ranking ordered by:

        1. Highest score
        2. Fastest completion time
        3. Lowest participant ID
        """
        trivia = self.trivia_repo.get_by_id(trivia_id)

        if not trivia:
            raise ResourceNotFoundException("Trivia not found.")

        participants = self.participant_repo.get_ranking(trivia_id)

        participants.sort(
            key=lambda participant: (
                -participant.score,
                self._get_completion_time_seconds(participant),
                participant.id,
            )
        )

        ranking: list[RankingItem] = []

        for position, participant in enumerate(participants, start=1):
            ranking.append(
                RankingItem(
                    position=position,
                    user_id=participant.user_id,
                    user_name=participant.user.name,
                    score=participant.score,
                    total_time_seconds=self._get_completion_time_seconds(
                        participant,
                    ),
                )
            )

        self.logger.info(
            "Ranking generated successfully: trivia_id=%s participants=%s",
            trivia_id,
            len(ranking),
        )

        return RankingResponse(
            trivia_id=trivia.id,
            trivia_name=trivia.name,
            ranking=ranking,
        )
