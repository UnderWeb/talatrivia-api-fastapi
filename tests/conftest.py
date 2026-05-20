# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.database import get_db
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.main import app
from app.models.enums import UserRole
from app.models.user import User

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# =========================================================
# DB LIFECYCLE (OPTIMIZED)
# =========================================================
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Create database schema once per test session.

    Ensures all tables exist before test execution starts,
    and are cleaned up after the session ends.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# =========================================================
# ISOLATED DB SESSION
# =========================================================
@pytest.fixture(scope="function")
def db_session():
    """
    Provides an isolated transactional database session per test.

    Uses SAVEPOINT-based nested transactions to ensure:
    - Test isolation
    - No state leakage between tests
    - Safe rollback after each test
    """
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested

        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()

        if transaction.is_active:
            transaction.rollback()

        connection.close()


# =========================================================
# FASTAPI CLIENT
# =========================================================
@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI test client with dependency overrides.

    Overrides database session dependency to use the
    isolated transactional session provided by db_session.
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# =========================================================
# USER FIXTURES
# =========================================================
@pytest.fixture
def admin_user(db_session):
    """
    Creates a persisted admin user for authenticated test scenarios.
    """
    user = User(
        name="Admin User",
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        role=UserRole.ADMIN,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def auth_header_admin(admin_user):
    """
    Generates a valid JWT authorization header for admin user.
    """
    token = create_access_token(
        {
            "sub": str(admin_user.id),
            "role": admin_user.role.value,
        }
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def player_user(db_session):
    """
    Creates a persisted player user for gameplay scenarios.
    """
    user = User(
        name="Player User",
        email="player@test.com",
        hashed_password=hash_password("player123"),
        role=UserRole.PLAYER,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def auth_header_player(player_user):
    """
    Generates a valid JWT authorization header for player user.
    """
    token = create_access_token(
        {
            "sub": str(player_user.id),
            "role": player_user.role.value,
        }
    )

    return {"Authorization": f"Bearer {token}"}
