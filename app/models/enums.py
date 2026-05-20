# app/models/enums.py
from enum import Enum


class UserRole(str, Enum):
    """
    Defines user access levels within the platform.
    """

    ADMIN = "admin"
    PLAYER = "player"


class DifficultyLevel(str, Enum):
    """
    Defines question difficulty and scoring weight.
    """

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    @property
    def points(self) -> int:
        """
        Return score value associated with difficulty level.
        """
        mapping = {
            DifficultyLevel.EASY: 1,
            DifficultyLevel.MEDIUM: 2,
            DifficultyLevel.HARD: 3,
        }

        return mapping[self]


class TriviaParticipantStatus(str, Enum):
    """
    Tracks the lifecycle of trivia participation.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
