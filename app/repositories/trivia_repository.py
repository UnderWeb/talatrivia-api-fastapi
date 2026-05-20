# app/repositories/trivia_repository.py
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.question import Question
from app.models.trivia import Trivia
from app.models.trivia_question import TriviaQuestion


class TriviaRepository:
    """
    Repository for trivia persistence operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, trivia: Trivia) -> Trivia:
        """
        Persist a trivia entity.
        """
        self.db.add(trivia)
        self.db.flush()

        return trivia

    def get_by_id(self, trivia_id: int) -> Trivia | None:
        """
        Retrieve trivia with ordered questions and options.
        """
        stmt = (
            select(Trivia)
            .where(Trivia.id == trivia_id)
            .options(
                selectinload(Trivia.questions)
                .joinedload(TriviaQuestion.question)
                .selectinload(Question.options)
            )
        )

        trivia = self.db.execute(stmt).scalar_one_or_none()

        if trivia:
            trivia.questions.sort(key=lambda trivia_question: trivia_question.position)

        return trivia

    def get_all(self) -> list[Trivia]:
        """
        Retrieve all trivias ordered by identifier.
        """
        stmt = select(Trivia).order_by(Trivia.id)

        return list(self.db.execute(stmt).scalars().all())
