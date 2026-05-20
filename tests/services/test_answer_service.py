# tests/services/test_answer_service.py
import pytest

from app.core.exceptions import BadRequestException, ConflictException
from app.models.answer import Answer
from app.models.enums import (
    DifficultyLevel,
    TriviaParticipantStatus,
)
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.trivia import Trivia
from app.models.trivia_participant import TriviaParticipant
from app.models.trivia_question import TriviaQuestion
from app.services.answer_service import AnswerService


def create_trivia_context(db_session, admin_user):
    """
    Create fully linked trivia gameplay context.
    """
    question = Question(
        text="What is SOLID?",
        difficulty=DifficultyLevel.EASY,
        options=[
            QuestionOption(
                text="Correct",
                is_correct=True,
            ),
            QuestionOption(
                text="Wrong",
                is_correct=False,
            ),
        ],
    )

    trivia = Trivia(name="Architecture Trivia", description="Testing")

    db_session.add_all(
        [
            question,
            trivia,
        ]
    )

    db_session.commit()

    trivia_question = TriviaQuestion(
        trivia_id=trivia.id,
        question_id=question.id,
        position=1,
    )

    participant = TriviaParticipant(
        user_id=admin_user.id,
        trivia_id=trivia.id,
    )

    db_session.add_all(
        [
            trivia_question,
            participant,
        ]
    )

    db_session.commit()

    return {
        "trivia": trivia,
        "question": question,
        "correct_option": question.options[0],
        "wrong_option": question.options[1],
        "participant": participant,
    }


def test_answer_service_submit_answer_returns_persisted_entity(db_session, admin_user):
    """
    AnswerService.submit_answer

    Requirement:
    Valid answer submission must persist an Answer entity.

    Expectation:
    Returns persisted answer linked to user, trivia and question.
    """
    context = create_trivia_context(db_session, admin_user)
    service = AnswerService(db_session)

    result = service.submit_answer(
        user_id=admin_user.id,
        trivia_id=context["trivia"].id,
        question_id=context["question"].id,
        selected_option_id=context["correct_option"].id,
    )

    assert isinstance(result, Answer)

    assert result.user_id == admin_user.id

    assert result.trivia_id == context["trivia"].id

    assert result.question_id == context["question"].id

    assert result.points_awarded > 0


def test_answer_service_prevents_duplicate_answers(db_session, admin_user):
    """
    AnswerService.submit_answer

    Requirement:
    Same question cannot be answered twice within the same trivia.

    Expectation:
    Raises ConflictException on duplicate submission.
    """
    context = create_trivia_context(db_session, admin_user)

    existing_answer = Answer(
        user_id=admin_user.id,
        trivia_id=context["trivia"].id,
        question_id=context["question"].id,
        selected_option_id=context["correct_option"].id,
        points_awarded=10,
    )

    db_session.add(existing_answer)
    db_session.commit()

    service = AnswerService(db_session)

    with pytest.raises(ConflictException):
        service.submit_answer(
            user_id=admin_user.id,
            trivia_id=context["trivia"].id,
            question_id=context["question"].id,
            selected_option_id=context["correct_option"].id,
        )


def test_answer_service_awards_points_for_correct_answer(db_session, admin_user):
    """
    AnswerService.submit_answer

    Requirement:
    Correct answers must award points.

    Expectation:
    points_awarded must be greater than zero.
    """
    context = create_trivia_context(db_session, admin_user)
    service = AnswerService(db_session)

    result = service.submit_answer(
        user_id=admin_user.id,
        trivia_id=context["trivia"].id,
        question_id=context["question"].id,
        selected_option_id=context["correct_option"].id,
    )

    assert result.points_awarded > 0


def test_answer_service_awards_zero_points_for_wrong_answer(db_session, admin_user):
    """
    AnswerService.submit_answer

    Requirement:
    Wrong answers must not award points.

    Expectation:
    points_awarded must equal zero.
    """
    context = create_trivia_context(db_session, admin_user)
    service = AnswerService(db_session)

    result = service.submit_answer(
        user_id=admin_user.id,
        trivia_id=context["trivia"].id,
        question_id=context["question"].id,
        selected_option_id=context["wrong_option"].id,
    )

    assert result.points_awarded == 0


def test_answer_service_requires_trivia_assignment(db_session, admin_user):
    """
    AnswerService.submit_answer

    Requirement:
    User must be assigned to trivia before answering.

    Expectation:
    Raises BadRequestException when participation does not exist.
    """
    context = create_trivia_context(db_session, admin_user)

    db_session.delete(context["participant"])
    db_session.commit()

    service = AnswerService(db_session)

    with pytest.raises(BadRequestException):
        service.submit_answer(
            user_id=admin_user.id,
            trivia_id=context["trivia"].id,
            question_id=context["question"].id,
            selected_option_id=context["correct_option"].id,
        )


def test_answer_service_rejects_question_not_in_trivia(db_session, admin_user):
    """
    AnswerService.submit_answer

    Requirement:
    Questions must belong to the target trivia.

    Expectation:
    Raises BadRequestException for unrelated questions.
    """
    context = create_trivia_context(db_session, admin_user)

    external_question = Question(
        text="External Question",
        difficulty=DifficultyLevel.EASY,
        options=[
            QuestionOption(
                text="Correct",
                is_correct=True,
            ),
            QuestionOption(
                text="Wrong",
                is_correct=False,
            ),
        ],
    )

    db_session.add(external_question)
    db_session.commit()

    service = AnswerService(db_session)

    with pytest.raises(BadRequestException):
        service.submit_answer(
            user_id=admin_user.id,
            trivia_id=context["trivia"].id,
            question_id=external_question.id,
            selected_option_id=external_question.options[0].id,
        )


def test_answer_service_rejects_invalid_option_for_question(db_session, admin_user):
    """
    AnswerService.submit_answer

    Requirement:
    Selected option must belong to the provided question.

    Expectation:
    Raises BadRequestException for invalid option mappings.
    """
    context = create_trivia_context(db_session, admin_user)

    another_question = Question(
        text="Another Question",
        difficulty=DifficultyLevel.EASY,
        options=[
            QuestionOption(
                text="Another Correct",
                is_correct=True,
            ),
            QuestionOption(
                text="Another Wrong",
                is_correct=False,
            ),
        ],
    )

    db_session.add(another_question)
    db_session.commit()

    service = AnswerService(db_session)

    with pytest.raises(BadRequestException):
        service.submit_answer(
            user_id=admin_user.id,
            trivia_id=context["trivia"].id,
            question_id=context["question"].id,
            selected_option_id=another_question.options[0].id,
        )


def test_answer_service_rejects_completed_trivia_answers(db_session, admin_user):
    """
    AnswerService.submit_answer

    Requirement:
    Completed trivia sessions must not accept new answers.

    Expectation:
    Raises BadRequestException for completed participations.
    """
    context = create_trivia_context(db_session, admin_user)
    participant = context["participant"]
    participant.status = TriviaParticipantStatus.COMPLETED

    db_session.commit()

    service = AnswerService(db_session)

    with pytest.raises(BadRequestException):
        service.submit_answer(
            user_id=admin_user.id,
            trivia_id=context["trivia"].id,
            question_id=context["question"].id,
            selected_option_id=context["correct_option"].id,
        )


def test_answer_service_starts_trivia_on_first_answer(db_session, admin_user):
    """
    AnswerService.submit_answer

    Requirement:
    First valid answer must automatically start trivia participation.

    Expectation:
    Participant status changes to IN_PROGRESS and started_at is populated.
    """
    context = create_trivia_context(db_session, admin_user)
    participant = context["participant"]

    assert participant.started_at is None

    assert participant.status == TriviaParticipantStatus.PENDING

    service = AnswerService(db_session)

    service.submit_answer(
        user_id=admin_user.id,
        trivia_id=context["trivia"].id,
        question_id=context["question"].id,
        selected_option_id=context["correct_option"].id,
    )

    db_session.refresh(participant)

    assert participant.started_at is not None

    assert participant.status == TriviaParticipantStatus.IN_PROGRESS
