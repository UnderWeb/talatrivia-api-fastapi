# app/repositories/question_repository.py
from collections.abc import Sequence

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, selectinload

from app.models.question import Question


class QuestionRepository:
    """
    Repository for question persistence operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, question: Question) -> Question:
        """
        Persist a new question entity.
        """
        self.db.add(question)
        self.db.flush()

        return question

    def get_by_id(self, question_id: int) -> Question | None:
        """
        Retrieve a question with its options.
        """
        stmt = (
            select(Question)
            .where(Question.id == question_id)
            .options(selectinload(Question.options))
        )

        return self.db.execute(stmt).scalar_one_or_none()

    def get_all(self) -> list[Question]:
        """
        Retrieve all questions ordered by identifier.
        """
        stmt = (
            select(Question)
            .options(selectinload(Question.options))
            .order_by(Question.id)
        )

        return list(self.db.execute(stmt).scalars().all())

    def get_by_ids(self, ids: Sequence[int]) -> list[Question]:
        """
        Retrieve multiple questions with eager-loaded options.
        """
        if not ids:
            return []

        stmt = (
            select(Question)
            .where(Question.id.in_(ids))
            .options(selectinload(Question.options))
        )

        questions = list(self.db.execute(stmt).scalars().all())
        question_map = {question.id: question for question in questions}

        return [
            question_map[question_id]
            for question_id in ids
            if question_id in question_map
        ]

    def exists_by_text(self, text: str) -> bool:
        """
        Check whether a question already exists.
        """
        stmt = select(exists().where(Question.text == text))

        return bool(self.db.execute(stmt).scalar())
