# app/schemas/trivia_participant.py
from datetime import datetime

from pydantic import Field

from app.models.enums import TriviaParticipantStatus

from .common import BaseSchema


class TriviaParticipantOut(BaseSchema):
    """
    Trivia participant representation.
    """

    id: int
    user_id: int
    trivia_id: int
    status: TriviaParticipantStatus
    score: int = Field(ge=0)
    started_at: datetime | None
    finished_at: datetime | None


class TriviaParticipantStatusOut(BaseSchema):
    """
    Current trivia gameplay status for a participant.
    """

    trivia_id: int
    status: TriviaParticipantStatus
    score: int = Field(ge=0)
    answered_questions: int = Field(ge=0)
    total_questions: int = Field(gt=0)
    completed: bool
