# app/schemas/trivia.py
from typing import Annotated

from pydantic import Field, field_validator, model_validator

from .common import BaseSchema
from .question import QuestionPublicOut


class TriviaCreate(BaseSchema):
    """
    Schema for trivia creation.
    """

    name: Annotated[str, Field(min_length=3, max_length=150)]
    description: Annotated[str | None, Field(max_length=500)] = None
    question_ids: Annotated[list[int], Field(min_length=1)]

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    @model_validator(mode="after")
    def validate_uniqueness(self) -> "TriviaCreate":
        if len(set(self.question_ids)) != len(self.question_ids):
            raise ValueError("Question IDs must be unique.")

        return self


class TriviaSummaryOut(BaseSchema):
    """
    Lightweight trivia representation.
    """

    id: int
    name: str
    description: str | None


class TriviaOut(BaseSchema):
    """
    Detailed trivia representation.
    """

    id: int
    name: str
    description: str | None
    questions: list[QuestionPublicOut] = Field(default_factory=list)
