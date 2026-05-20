# app/models/__init__.py
"""Model registry for SQLAlchemy metadata loading."""

from app.models.answer import Answer  # noqa: F401
from app.models.question import Question  # noqa: F401
from app.models.question_option import QuestionOption  # noqa: F401
from app.models.trivia import Trivia  # noqa: F401
from app.models.trivia_participant import TriviaParticipant  # noqa: F401
from app.models.trivia_question import TriviaQuestion  # noqa: F401
from app.models.user import User  # noqa: F401
