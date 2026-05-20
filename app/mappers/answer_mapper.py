# app/mappers/answer_mapper.py
from app.models.answer import Answer
from app.schemas.answer import AnswerOut


class AnswerMapper:
    """
    Mapper for answer API representations.
    """

    @staticmethod
    def to_out(answer: Answer) -> AnswerOut:
        """
        Map answer entity to response schema.
        """
        return AnswerOut(
            id=answer.id,
            trivia_id=answer.trivia_id,
            question_id=answer.question_id,
            selected_option_id=answer.selected_option_id,
            points_awarded=answer.points_awarded,
        )
