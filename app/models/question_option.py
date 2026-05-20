# app/models/question_option.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from .question import Question


class QuestionOption(Base, TimestampMixin):
    """
    Represents a selectable answer option for a question.
    """

    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        comment="Option text displayed to the player",
    )
    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this option is the correct answer",
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[Question] = relationship(
        "Question",
        back_populates="options",
    )
