# app/api/dependencies/database.py
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Provide a scoped SQLAlchemy session per request.

    The session lifecycle is managed by FastAPI dependencies.
    Transaction boundaries are handled explicitly at the service layer.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
