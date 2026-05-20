# app/schemas/answer.py
from pydantic import Field

from .common import BaseSchema


class AnswerCreate(BaseSchema):
    """
    Input schema for answer submission.
    """

    trivia_id: int = Field(gt=0)
    question_id: int = Field(gt=0)
    selected_option_id: int = Field(gt=0)


class AnswerOut(BaseSchema):
    """
    Answer submission response schema.
    """

    id: int
    trivia_id: int
    question_id: int
    selected_option_id: int
    points_awarded: int = Field(ge=0)
