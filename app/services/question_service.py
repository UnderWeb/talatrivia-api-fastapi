# app/services/question_service.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ResourceNotFoundException,
)
from app.models.enums import DifficultyLevel
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionOptionCreate

from .base_service import BaseService


class QuestionService(BaseService):
    """
    Question management service.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(db)
        self.question_repo = QuestionRepository(db)

    def create_question(
        self,
        text: str,
        difficulty: DifficultyLevel,
        options: list[QuestionOptionCreate],
    ) -> Question:
        """
        Create a trivia question.
        """
        normalized_text = text.strip()

        if self.question_repo.exists_by_text(normalized_text):
            raise ConflictException("Question already exists.")

        correct_options_count = sum(1 for option in options if option.is_correct)

        if correct_options_count != 1:
            raise BadRequestException(
                "Question must contain exactly one correct option."
            )

        unique_options = {option.text.strip().lower() for option in options}

        if len(unique_options) != len(options):
            raise BadRequestException("Question options must be unique.")

        try:
            question = Question(
                text=normalized_text,
                difficulty=difficulty,
            )

            question.options.extend(
                [
                    QuestionOption(
                        text=option.text.strip(),
                        is_correct=option.is_correct,
                    )
                    for option in options
                ]
            )

            created_question = self.question_repo.create(question)
            self.commit()

            self.logger.info(
                "Question created successfully: question_id=%s",
                created_question.id,
            )

            return created_question
        except IntegrityError as exc:
            self.rollback()
            raise ConflictException("Question already exists.") from exc
        except Exception:
            self.rollback()
            raise

    def get_by_id(self, question_id: int) -> Question:
        """
        Retrieve question by ID.
        """
        question = self.question_repo.get_by_id(question_id)

        if not question:
            raise ResourceNotFoundException("Question not found.")

        return question

    def get_all(self) -> list[Question]:
        """
        Retrieve all questions.
        """
        return self.question_repo.get_all()
