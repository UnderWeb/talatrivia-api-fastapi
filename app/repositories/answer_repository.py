# app/repositories/answer_repository.py
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.models.answer import Answer


class AnswerRepository:
    """
    Repository for answer persistence operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, answer: Answer) -> Answer:
        """
        Persist a new answer entity.
        """
        self.db.add(answer)
        self.db.flush()

        return answer

    def get_by_id(self, answer_id: int) -> Answer | None:
        """
        Retrieve answer by identifier.
        """
        return self.db.get(Answer, answer_id)

    def exists_answer(self, user_id: int, trivia_id: int, question_id: int) -> bool:
        """
        Check whether a user already answered a question in a trivia.
        """
        stmt = select(
            exists().where(
                Answer.user_id == user_id,
                Answer.trivia_id == trivia_id,
                Answer.question_id == question_id,
            )
        )

        return bool(self.db.execute(stmt).scalar_one())
