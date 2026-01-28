import pytest
import os
import requests
import json

@pytest.fixture(scope="session")
def base_url():
    # Allow overriding via env var, validation could be added here
    return os.getenv("API_BASE_URL", "https://master.suprabhatapp.in/rest/suprabhat/V2")

@pytest.fixture(scope="session")
def auth_token(base_url):
    # Token Generator API: Get Auth Token
    url = f'{base_url}/getAuthToken'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"login.username": "invoice2", "login.password": "vst123", "tenantId": "suprabhat-latest"}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code not in [200, 201]:
        return None
    
    data = response.json()
    # Try to extract token
    token = data.get('authToken') or data.get('token') or data.get('access_token')
    return token
