# app/db/base.py
"""SQLAlchemy base model declaration."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass
