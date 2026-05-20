# app/api/routes/trivias.py
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, require_admin
from app.api.dependencies.database import get_db
from app.mappers.trivia_mapper import TriviaMapper
from app.models.user import User
from app.schemas.ranking import RankingResponse
from app.schemas.trivia import TriviaCreate, TriviaOut, TriviaSummaryOut
from app.services.ranking_service import RankingService
from app.services.trivia_service import TriviaService

router = APIRouter(prefix="/trivias", tags=["trivias"])


def get_trivia_service(db: Session = Depends(get_db)) -> TriviaService:
    """
    Dependency provider for TriviaService.
    """
    return TriviaService(db)


def get_ranking_service(db: Session = Depends(get_db)) -> RankingService:
    """
    Dependency provider for RankingService.
    """
    return RankingService(db)


@router.post("/", response_model=TriviaOut, status_code=status.HTTP_201_CREATED)
def create_trivia(
    payload: TriviaCreate,
    _: User = Depends(require_admin),
    service: TriviaService = Depends(get_trivia_service),
) -> TriviaOut:
    """
    Create a trivia with assigned questions and participants.

    Restricted to admin users.
    """
    trivia = service.create_trivia(
        name=payload.name,
        description=payload.description,
        question_ids=payload.question_ids,
    )

    return TriviaMapper.to_out(trivia)


@router.get("/", response_model=list[TriviaSummaryOut], status_code=status.HTTP_200_OK)
def list_trivias(
    _: User = Depends(get_current_user),
    service: TriviaService = Depends(get_trivia_service),
) -> list[TriviaSummaryOut]:
    """
    Retrieve all available trivias for the authenticated user.
    """
    trivias = service.get_all()

    return TriviaMapper.to_summary_out_list(trivias)


@router.get("/{trivia_id}", response_model=TriviaOut, status_code=status.HTTP_200_OK)
def get_trivia(
    trivia_id: int,
    _: User = Depends(get_current_user),
    service: TriviaService = Depends(get_trivia_service),
) -> TriviaOut:
    """
    Retrieve trivia details.
    """
    trivia = service.get_by_id(trivia_id)

    return TriviaMapper.to_out(trivia)


@router.get(
    "/{trivia_id}/ranking",
    response_model=RankingResponse,
    status_code=status.HTTP_200_OK,
)
def get_trivia_ranking(
    trivia_id: int,
    _: User = Depends(get_current_user),
    service: RankingService = Depends(get_ranking_service),
) -> RankingResponse:
    """
    Retrieve trivia ranking ordered by score and completion time.
    """
    return service.get_trivia_ranking(trivia_id)


@router.post("/{trivia_id}/join", status_code=status.HTTP_201_CREATED)
def join_trivia(
    trivia_id: int,
    user: User = Depends(get_current_user),
    service: TriviaService = Depends(get_trivia_service),
) -> dict:
    """
    Join a trivia session (start playing).
    """

    participant = service.join_trivia(trivia_id=trivia_id, user_id=user.id)

    return {
        "trivia_id": participant.trivia_id,
        "status": participant.status,
        "started_at": participant.started_at,
        "score": participant.score,
    }
