# app/mappers/trivia_mapper.py
from app.models.trivia import Trivia
from app.schemas.trivia import TriviaOut, TriviaSummaryOut

from .question_mapper import QuestionMapper


class TriviaMapper:
    """
    Mapper for trivia API representations.
    """

    @staticmethod
    def to_summary_out(trivia: Trivia) -> TriviaSummaryOut:
        """
        Map Trivia model to lightweight response schema.
        """
        return TriviaSummaryOut(
            id=trivia.id,
            name=trivia.name,
            description=trivia.description,
        )

    @staticmethod
    def to_summary_out_list(trivias: list[Trivia]) -> list[TriviaSummaryOut]:
        """
        Map trivia entity list to summary response schema list.
        """
        return [TriviaMapper.to_summary_out(trivia) for trivia in trivias]

    @staticmethod
    def to_out(trivia: Trivia) -> TriviaOut:
        """
        Map trivia entity to detailed response schema.
        """
        ordered_questions = sorted(trivia.questions, key=lambda item: item.position)

        return TriviaOut(
            id=trivia.id,
            name=trivia.name,
            description=trivia.description,
            questions=[
                QuestionMapper.to_public_out(trivia_question.question)
                for trivia_question in ordered_questions
            ],
        )

    @staticmethod
    def to_out_list(trivias: list[Trivia]) -> list[TriviaOut]:
        """
        Map trivia entity list to detailed response schema list.
        """
        return [TriviaMapper.to_out(trivia) for trivia in trivias]
