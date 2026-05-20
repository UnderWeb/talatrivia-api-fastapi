# tests/repositories/test_user_repository.py
from app.models.user import User
from app.repositories.user_repository import UserRepository


def test_user_repository_create_and_get_by_id(db_session):
    """
    UserRepository.create + get_by_id

    Requirement:
    The repository must persist a User entity and allow retrieval by ID.

    Expectation:
    The same entity must be retrievable with consistent data.
    """
    repo = UserRepository(db_session)

    user = User(
        name="Repo User",
        email="repo@test.com",
        hashed_password="hashed-password",
    )

    created_user = repo.create(user)
    db_session.commit()

    fetched_user = repo.get_by_id(created_user.id)

    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.email == "repo@test.com"


def test_user_repository_get_by_email_success(db_session):
    """
    UserRepository.get_by_email

    Requirement:
    The repository must retrieve users by unique email.

    Expectation:
    Returns the correct user when email exists.
    """
    repo = UserRepository(db_session)

    email = "repo_test@example.com"

    db_session.add(
        User(
            name="Test User",
            email=email,
            hashed_password="hashed",
        )
    )
    db_session.commit()

    user = repo.get_by_email(email)

    assert user is not None
    assert user.email == email


def test_user_repository_get_by_email_returns_none(db_session):
    """
    UserRepository.get_by_email

    Requirement:
    Non-existent emails must return None.

    Expectation:
    Repository should return None for unknown email.
    """
    repo = UserRepository(db_session)

    user = repo.get_by_email("unknown@test.com")

    assert user is None
