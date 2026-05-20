# app/models/question.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

from .enums import DifficultyLevel

if TYPE_CHECKING:
    from .question_option import QuestionOption


class Question(Base, TimestampMixin):
    """
    Represents a trivia question.
    """

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    text: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Question text displayed to players",
    )
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(
            DifficultyLevel,
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        index=True,
        comment="Question difficulty level",
    )
    options: Mapped[list[QuestionOption]] = relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    __table_args__ = (UniqueConstraint("text", name="uq_question_text"),)
