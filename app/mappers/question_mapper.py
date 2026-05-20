# app/mappers/question_mapper.py
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.schemas.question import (
    QuestionAdminOut,
    QuestionOptionAdminOut,
    QuestionOptionOut,
    QuestionPublicOut,
)


class QuestionMapper:
    """
    Mapper for question API representations.
    """

    @staticmethod
    def to_option_out(option: QuestionOption) -> QuestionOptionOut:
        """
        Map question option to public schema.
        """
        return QuestionOptionOut(id=option.id, text=option.text)

    @staticmethod
    def to_option_admin_out(option: QuestionOption) -> QuestionOptionAdminOut:
        """
        Map question option to admin schema.
        """
        return QuestionOptionAdminOut(
            id=option.id,
            text=option.text,
            is_correct=option.is_correct,
        )

    @staticmethod
    def to_public_out(question: Question) -> QuestionPublicOut:
        """
        Map question entity to public response schema.
        """
        return QuestionPublicOut(
            id=question.id,
            text=question.text,
            options=[
                QuestionMapper.to_option_out(option) for option in question.options
            ],
        )

    @staticmethod
    def to_public_out_list(questions: list[Question]) -> list[QuestionPublicOut]:
        """
        Map question entity list to public response schema list.
        """
        return [QuestionMapper.to_public_out(question) for question in questions]

    @staticmethod
    def to_admin_out(question: Question) -> QuestionAdminOut:
        """
        Map question entity to admin response schema.
        """
        return QuestionAdminOut(
            id=question.id,
            text=question.text,
            difficulty=question.difficulty,
            options=[
                QuestionMapper.to_option_admin_out(option)
                for option in question.options
            ],
        )

    @staticmethod
    def to_admin_out_list(questions: list[Question]) -> list[QuestionAdminOut]:
        """
        Map question entity list to admin response schema list.
        """
        return [QuestionMapper.to_admin_out(question) for question in questions]
