# app/models/trivia_participant.py
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

from .enums import TriviaParticipantStatus

if TYPE_CHECKING:
    from .trivia import Trivia
    from .user import User


class TriviaParticipant(Base, TimestampMixin):
    """
    Represents a user's participation in a trivia session.
    """

    __tablename__ = "trivia_participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    trivia_id: Mapped[int] = mapped_column(
        ForeignKey("trivias.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[TriviaParticipantStatus] = mapped_column(
        Enum(
            TriviaParticipantStatus,
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=TriviaParticipantStatus.PENDING,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    user: Mapped[User] = relationship("User", back_populates="participations")
    trivia: Mapped[Trivia] = relationship("Trivia", back_populates="participants")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "trivia_id",
            name="uq_user_trivia",
        ),
        CheckConstraint(
            "score >= 0",
            name="ck_trivia_participant_score_positive",
        ),
    )
