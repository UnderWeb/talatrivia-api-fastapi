# app/schemas/question.py
from typing import Annotated

from pydantic import Field, field_validator, model_validator

from app.models.enums import DifficultyLevel

from .common import BaseSchema


class QuestionOptionOut(BaseSchema):
    """
    Public question option schema.
    """

    id: int
    text: str


class QuestionOptionAdminOut(BaseSchema):
    """
    Administrative question option schema.
    """

    id: int
    text: str
    is_correct: bool


class QuestionOptionCreate(BaseSchema):
    """
    Schema for question option creation.
    """

    text: Annotated[str, Field(min_length=1, max_length=300)]
    is_correct: bool

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()


class QuestionCreate(BaseSchema):
    """
    Schema for question creation.
    """

    text: Annotated[str, Field(min_length=5, max_length=500)]
    difficulty: DifficultyLevel
    options: Annotated[list[QuestionOptionCreate], Field(min_length=2, max_length=6)]

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_options(self) -> "QuestionCreate":
        correct_options = [option for option in self.options if option.is_correct]

        if len(correct_options) != 1:
            raise ValueError("Question must contain exactly one correct option.")

        normalized_texts = {option.text.strip().lower() for option in self.options}

        if len(normalized_texts) != len(self.options):
            raise ValueError("Question options must be unique.")

        return self


class QuestionPublicOut(BaseSchema):
    """
    Public question representation for players.
    """

    id: int
    text: str
    options: list[QuestionOptionOut]


class QuestionAdminOut(BaseSchema):
    """
    Administrative question representation.
    """

    id: int
    text: str
    difficulty: DifficultyLevel
    options: list[QuestionOptionAdminOut]
