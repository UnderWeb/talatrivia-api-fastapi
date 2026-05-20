# app/models/answer.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from .question import Question
    from .question_option import QuestionOption
    from .trivia import Trivia
    from .user import User


class Answer(Base, TimestampMixin):
    """
    Represents a user's submitted answer for a trivia question.

    Points are persisted at submission time to preserve historical integrity,
    even if question difficulty changes later.
    """

    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    trivia_id: Mapped[int] = mapped_column(
        ForeignKey("trivias.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    selected_option_id: Mapped[int] = mapped_column(
        ForeignKey("question_options.id", ondelete="CASCADE"),
        nullable=False,
    )
    points_awarded: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Points earned for this answer",
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="answers",
    )
    question: Mapped[Question] = relationship("Question")
    trivia: Mapped[Trivia] = relationship("Trivia")
    selected_option: Mapped[QuestionOption] = relationship("QuestionOption")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "trivia_id",
            "question_id",
            name="uq_user_trivia_question_answer",
        ),
        CheckConstraint(
            "points_awarded >= 0",
            name="ck_answers_points_awarded_positive",
        ),
        Index(
            "ix_answers_trivia_user",
            "trivia_id",
            "user_id",
        ),
    )
