import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.core.cache import get_cache
import redis
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv()

# Test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/webhook_test")
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")

@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL)
    return engine

@pytest.fixture(scope="session")
def test_db(test_engine):
    """Create test database tables."""
    from app.models.models import Base
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_db):
    """Create a fresh database session for each test."""
    connection = test_db.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create a test client with a fresh database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def test_redis():
    """Create a test Redis connection."""
    redis_client = redis.from_url(TEST_REDIS_URL)
    yield redis_client
    redis_client.flushdb() 