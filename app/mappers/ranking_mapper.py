# app/mappers/ranking_mapper.py
from app.models.trivia import Trivia
from app.models.trivia_participant import TriviaParticipant
from app.schemas.ranking import RankingItem, RankingResponse


class RankingMapper:
    """
    Mapper for trivia ranking representations.
    """

    @staticmethod
    def to_ranking_item(
        participant: TriviaParticipant,
        position: int,
        total_time_seconds: int | None,
    ) -> RankingItem:
        """
        Map participant to ranking item schema.
        """
        return RankingItem(
            position=position,
            user_id=participant.user_id,
            user_name=participant.user.name,
            score=participant.score,
            total_time_seconds=total_time_seconds,
        )

    @staticmethod
    def to_ranking_response(
        trivia: Trivia, ranking: list[RankingItem]
    ) -> RankingResponse:
        """
        Map trivia ranking response.
        """
        return RankingResponse(
            trivia_id=trivia.id,
            trivia_name=trivia.name,
            ranking=ranking,
        )
