import pytest
import os
import requests
import json

@pytest.fixture(scope="session")
def base_url():
    # Allow overriding via env var, validation could be added here
    return os.getenv("API_BASE_URL", "https://master.suprabhatapp.in")

@pytest.fixture(scope="session")
def auth_token(base_url):
    # Token Generator API: getAuthToken
    url = f'{base_url}/rest/suprabhat/V2/getAuthToken'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    json_body = {}
    response = requests.post(url, headers=headers, json=json_body)
    if response.status_code not in [200, 201]:
        return None
    
    data = response.json()
    # Try to extract token
    token = data.get('token') or data.get('token') or data.get('access_token')
    return token
