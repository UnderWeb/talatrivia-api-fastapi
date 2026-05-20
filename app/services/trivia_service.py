# app/services/trivia_service.py
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ResourceNotFoundException,
)
from app.models.enums import TriviaParticipantStatus
from app.models.trivia import Trivia
from app.models.trivia_participant import TriviaParticipant
from app.models.trivia_question import TriviaQuestion
from app.repositories.question_repository import QuestionRepository
from app.repositories.trivia_repository import TriviaRepository
from app.repositories.user_repository import UserRepository

from .base_service import BaseService


class TriviaService(BaseService):
    """
    Trivia management service.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.trivia_repo = TriviaRepository(db)
        self.question_repo = QuestionRepository(db)
        self.user_repo = UserRepository(db)

    def create_trivia(
        self,
        name: str,
        description: str | None,
        question_ids: list[int],
    ) -> Trivia:
        """
        Create trivia with questions and participants.
        """
        if len(set(question_ids)) != len(question_ids):
            raise BadRequestException("Question IDs must be unique.")

        questions = self.question_repo.get_by_ids(question_ids)

        if len(questions) != len(question_ids):
            raise ResourceNotFoundException("One or more questions were not found.")

        try:
            trivia = Trivia(name=name.strip(), description=description)

            trivia.questions.extend(
                [
                    TriviaQuestion(
                        question_id=question_id,
                        position=index + 1,
                    )
                    for index, question_id in enumerate(question_ids)
                ]
            )

            created_trivia = self.trivia_repo.create(trivia)

            self.commit()

            persisted_trivia = self.trivia_repo.get_by_id(
                created_trivia.id,
            )

            if not persisted_trivia:
                raise ResourceNotFoundException(
                    "Trivia not found after creation.",
                )

            self.logger.info(
                "Trivia created successfully: trivia_id=%s",
                persisted_trivia.id,
            )

            return persisted_trivia
        except IntegrityError as exc:
            self.rollback()
            raise ConflictException("Trivia creation conflict.") from exc
        except Exception:
            self.rollback()
            raise

    def get_by_id(self, trivia_id: int) -> Trivia:
        """
        Retrieve trivia by ID.
        """
        trivia = self.trivia_repo.get_by_id(trivia_id)

        if not trivia:
            raise ResourceNotFoundException("Trivia not found.")

        return trivia

    def get_all(self) -> list[Trivia]:
        """
        Retrieve all trivias.
        """
        return self.trivia_repo.get_all()

    def join_trivia(self, trivia_id: int, user_id: int) -> TriviaParticipant:
        """
        Join a trivia session (idempotent).
        """

        trivia = self.trivia_repo.get_by_id(trivia_id)

        if not trivia:
            raise ResourceNotFoundException("Trivia not found.")

        participant = (
            self.db.query(TriviaParticipant)
            .filter_by(trivia_id=trivia_id, user_id=user_id)
            .first()
        )

        if participant:
            return participant

        participant = TriviaParticipant(
            trivia_id=trivia_id,
            user_id=user_id,
            status=TriviaParticipantStatus.IN_PROGRESS,
            started_at=datetime.now(timezone.utc),
            score=0,
        )

        self.db.add(participant)
        self.commit()

        self.logger.info(
            "User joined trivia: user_id=%s trivia_id=%s",
            user_id,
            trivia_id,
        )

        return participant
