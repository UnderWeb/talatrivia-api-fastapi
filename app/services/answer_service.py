# app/services/answer_service.py
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ResourceNotFoundException,
)
from app.models.answer import Answer
from app.models.enums import TriviaParticipantStatus
from app.repositories.answer_repository import AnswerRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.trivia_participant_repository import TriviaParticipantRepository
from app.repositories.trivia_repository import TriviaRepository

from .base_service import BaseService


class AnswerService(BaseService):
    """
    Trivia gameplay answer service.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.answer_repo = AnswerRepository(db)
        self.question_repo = QuestionRepository(db)
        self.participant_repo = TriviaParticipantRepository(db)
        self.trivia_repo = TriviaRepository(db)

    def submit_answer(
        self,
        user_id: int,
        trivia_id: int,
        question_id: int,
        selected_option_id: int,
    ) -> Answer:
        """
        Submit answer for a trivia question.
        """
        participant = self.participant_repo.get_by_user_and_trivia(
            user_id=user_id,
            trivia_id=trivia_id,
        )

        if not participant:
            raise BadRequestException("User is not assigned to this trivia.")

        if participant.status == TriviaParticipantStatus.COMPLETED:
            raise BadRequestException("Trivia already completed.")

        trivia = self.trivia_repo.get_by_id(trivia_id)

        if not trivia:
            raise ResourceNotFoundException("Trivia not found.")

        trivia_question_ids = {
            trivia_question.question_id for trivia_question in trivia.questions
        }

        if question_id not in trivia_question_ids:
            raise BadRequestException("Question does not belong to trivia.")

        if self.answer_repo.exists_answer(
            user_id=user_id,
            trivia_id=trivia_id,
            question_id=question_id,
        ):
            raise ConflictException("Question already answered.")

        question = self.question_repo.get_by_id(question_id)

        if not question:
            raise ResourceNotFoundException("Question not found.")

        selected_option = next(
            (option for option in question.options if option.id == selected_option_id),
            None,
        )

        if not selected_option:
            raise BadRequestException("Invalid option for question.")

        awarded_points = question.difficulty.points if selected_option.is_correct else 0

        try:
            answer = Answer(
                user_id=user_id,
                trivia_id=trivia_id,
                question_id=question_id,
                selected_option_id=selected_option_id,
                points_awarded=awarded_points,
            )

            created_answer = self.answer_repo.create(answer)
            participant.score += awarded_points

            if participant.started_at is None:
                participant.started_at = datetime.now(
                    timezone.utc,
                )

                participant.status = TriviaParticipantStatus.IN_PROGRESS

            self.commit()

            self.logger.info(
                "Answer submitted successfully: answer_id=%s",
                created_answer.id,
            )

            return created_answer
        except IntegrityError as exc:
            self.rollback()
            raise ConflictException("Answer already submitted.") from exc
        except Exception:
            self.rollback()
            raise

    def complete_trivia(self, user_id: int, trivia_id: int) -> None:
        """
        Complete trivia participation.
        """
        participant = self.participant_repo.get_by_user_and_trivia(
            user_id=user_id,
            trivia_id=trivia_id,
        )

        if not participant:
            raise ResourceNotFoundException("Trivia participation not found.")

        if participant.status == TriviaParticipantStatus.COMPLETED:
            return

        participant.status = TriviaParticipantStatus.COMPLETED
        participant.finished_at = datetime.now(timezone.utc)

        try:
            self.commit()

            self.logger.info(
                "Trivia completed successfully: trivia_id=%s user_id=%s",
                trivia_id,
                user_id,
            )

        except Exception:
            self.rollback()
            raise
