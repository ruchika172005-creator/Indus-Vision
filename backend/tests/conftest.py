import pytest
from app.database.init_db import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensures database and demo samples are created before tests execute."""
    init_db()
    yield
