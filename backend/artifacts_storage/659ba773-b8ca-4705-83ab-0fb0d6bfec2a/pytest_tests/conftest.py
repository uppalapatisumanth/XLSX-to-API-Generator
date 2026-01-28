import pytest
import os
import requests
import json

@pytest.fixture(scope="session")
def base_url():
    # Allow overriding via env var, validation could be added here
    return os.getenv("API_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def auth_token(base_url):
    # No Token Generator API found. 
    # Configure via env var if needed.
    return os.getenv("AUTH_TOKEN", None)
