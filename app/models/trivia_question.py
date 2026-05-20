# app/models/trivia_question.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from .question import Question
    from .trivia import Trivia


class TriviaQuestion(Base, TimestampMixin):
    """
    Association model between trivias and questions.

    Maintains deterministic question ordering inside a trivia.
    """

    __tablename__ = "trivia_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    trivia_id: Mapped[int] = mapped_column(
        ForeignKey("trivias.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    trivia: Mapped[Trivia] = relationship("Trivia", back_populates="questions")
    question: Mapped[Question] = relationship("Question")

    __table_args__ = (
        UniqueConstraint(
            "trivia_id",
            "question_id",
            name="uq_trivia_question",
        ),
        UniqueConstraint(
            "trivia_id",
            "position",
            name="uq_trivia_question_position",
        ),
        CheckConstraint(
            "position > 0",
            name="ck_trivia_question_position_positive",
        ),
    )
