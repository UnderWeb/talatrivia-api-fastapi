# app/api/routes/questions.py
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import require_admin
from app.api.dependencies.database import get_db
from app.mappers.question_mapper import QuestionMapper
from app.models.user import User
from app.schemas.question import (
    QuestionAdminOut,
    QuestionCreate,
    QuestionPublicOut,
)
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


def get_question_service(db: Session = Depends(get_db)) -> QuestionService:
    """
    Dependency provider for QuestionService.
    """
    return QuestionService(db)


@router.post("/", response_model=QuestionAdminOut, status_code=status.HTTP_201_CREATED)
def create_question(
    payload: QuestionCreate,
    _: User = Depends(require_admin),
    service: QuestionService = Depends(get_question_service),
) -> QuestionAdminOut:
    """
    Create a new trivia question.

    Restricted to admin users.
    """
    question = service.create_question(
        text=payload.text,
        difficulty=payload.difficulty,
        options=payload.options,
    )

    return QuestionMapper.to_admin_out(question)


@router.get("/", response_model=list[QuestionPublicOut], status_code=status.HTTP_200_OK)
def list_questions(
    service: QuestionService = Depends(get_question_service),
) -> list[QuestionPublicOut]:
    """
    List questions for players.

    Correct answers and difficulty metadata are intentionally hidden.
    """
    questions = service.get_all()

    return QuestionMapper.to_public_out_list(questions)


@router.get(
    "/{question_id}", response_model=QuestionPublicOut, status_code=status.HTTP_200_OK
)
def get_question(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
) -> QuestionPublicOut:
    """
    Retrieve public trivia question.
    """
    question = service.get_by_id(question_id)

    return QuestionMapper.to_public_out(question)


@router.get(
    "/admin", response_model=list[QuestionAdminOut], status_code=status.HTTP_200_OK
)
def admin_list_questions(
    _: User = Depends(require_admin),
    service: QuestionService = Depends(get_question_service),
) -> list[QuestionAdminOut]:
    """
    List questions with administrative metadata.

    Restricted to admin users.
    """
    questions = service.get_all()

    return QuestionMapper.to_admin_out_list(questions)


@router.get(
    "/admin/{question_id}",
    response_model=QuestionAdminOut,
    status_code=status.HTTP_200_OK,
)
def admin_get_question(
    question_id: int,
    _: User = Depends(require_admin),
    service: QuestionService = Depends(get_question_service),
) -> QuestionAdminOut:
    """
    Retrieve question with administrative metadata.

    Restricted to admin users.
    """
    question = service.get_by_id(question_id)

    return QuestionMapper.to_admin_out(question)
