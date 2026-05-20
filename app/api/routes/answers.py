# app/api/routes/answers.py
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.mappers.answer_mapper import AnswerMapper
from app.models.user import User
from app.schemas.answer import AnswerCreate, AnswerOut
from app.services.answer_service import AnswerService

router = APIRouter(prefix="/answers", tags=["Answers"])
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_answer_service(db: Session = Depends(get_db)) -> AnswerService:
    """
    Dependency provider for AnswerService.
    """
    return AnswerService(db)


@router.post("/", response_model=AnswerOut, status_code=status.HTTP_201_CREATED)
def submit_answer(
    payload: AnswerCreate,
    current_user: CurrentUser,
    service: AnswerService = Depends(get_answer_service),
) -> AnswerOut:
    """
    Submit an answer for a trivia question.
    """
    answer = service.submit_answer(
        user_id=current_user.id,
        trivia_id=payload.trivia_id,
        question_id=payload.question_id,
        selected_option_id=payload.selected_option_id,
    )

    return AnswerMapper.to_out(answer)


@router.post("/complete/{trivia_id}", status_code=status.HTTP_204_NO_CONTENT)
def complete_trivia(
    trivia_id: int,
    current_user: CurrentUser,
    service: AnswerService = Depends(get_answer_service),
) -> None:
    """
    Finalize trivia participation for the authenticated user.
    """
    service.complete_trivia(
        user_id=current_user.id,
        trivia_id=trivia_id,
    )
