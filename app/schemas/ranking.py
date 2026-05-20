# app/schemas/ranking.py
from pydantic import Field

from .common import BaseSchema


class RankingItem(BaseSchema):
    """
    Represents a participant ranking entry.
    """

    position: int = Field(gt=0)
    user_id: int
    user_name: str
    score: int = Field(ge=0)
    total_time_seconds: int | None = Field(default=None, ge=0)


class RankingResponse(BaseSchema):
    """
    Trivia ranking response.
    """

    trivia_id: int
    trivia_name: str
    ranking: list[RankingItem]
