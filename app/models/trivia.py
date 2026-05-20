# app/models/trivia.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from .trivia_participant import TriviaParticipant
    from .trivia_question import TriviaQuestion


class Trivia(Base, TimestampMixin):
    """
    Represents a trivia game entity.
    """

    __tablename__ = "trivias"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Trivia display name",
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional trivia description",
    )
    questions: Mapped[list[TriviaQuestion]] = relationship(
        "TriviaQuestion",
        back_populates="trivia",
        cascade="all, delete-orphan",
    )
    participants: Mapped[list[TriviaParticipant]] = relationship(
        "TriviaParticipant",
        back_populates="trivia",
        cascade="all, delete-orphan",
    )
