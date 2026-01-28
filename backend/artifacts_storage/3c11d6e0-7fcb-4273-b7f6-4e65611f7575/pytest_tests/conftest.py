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
    # Token Generator API: fetchEmplLeaveRequestList
    url = f'{base_url}/rest/v2/dailybiz/fetchEmplLeaveRequestList'
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code not in [200, 201]:
        return None
    
    data = response.json()
    # Try to extract token
    token = data.get('token') or data.get('token') or data.get('access_token')
    return token
