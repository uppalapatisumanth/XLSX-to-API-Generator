import pytest
import os

@pytest.fixture(scope="session")
def base_url():
    # Allow overriding via env var, validation could be added here
    return os.getenv("API_BASE_URL", "http://localhost:8000")
