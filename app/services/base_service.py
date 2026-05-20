# app/services/base_service.py
from sqlalchemy.orm import Session

from app.core.logger import get_logger


class BaseService:
    """
    Base service with shared transactional utilities.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.logger = get_logger(self.__class__.__name__)

    def commit(self) -> None:
        """
        Commit current transaction.
        """

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def rollback(self) -> None:
        """
        Rollback current transaction.
        """

        self.db.rollback()
