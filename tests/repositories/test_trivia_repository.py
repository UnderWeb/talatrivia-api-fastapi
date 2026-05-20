# tests/repositories/test_trivia_repository.py
from app.models.trivia import Trivia
from app.repositories.trivia_repository import TriviaRepository


def test_trivia_repository_create_and_get(
    db_session,
):
    """
    TriviaRepository.create + get_by_id

    Requirement:
    Trivias must persist correctly.

    Expectation:
    Trivia is retrievable by ID.
    """
    repo = TriviaRepository(db_session)
    trivia = Trivia(name="Test Trivia", description="Repository test")
    created = repo.create(trivia)

    db_session.commit()

    fetched = repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Test Trivia"
    assert fetched.description == "Repository test"
