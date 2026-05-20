# app/models/user.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

from .enums import UserRole

if TYPE_CHECKING:
    from .answer import Answer
    from .trivia_participant import TriviaParticipant


class User(Base, TimestampMixin):
    """
    Represents a registered TalaTrivia user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="User full name",
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique email address",
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Argon2 hashed password",
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=UserRole.PLAYER,
        index=True,
    )

    answers: Mapped[list[Answer]] = relationship(
        "Answer",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    participations: Mapped[list[TriviaParticipant]] = relationship(
        "TriviaParticipant",
        back_populates="user",
        cascade="all, delete-orphan",
    )
