import pytest
import requests

def test_getuserdetails(base_url):
    url = f"{base_url}/rest/suprabhat/V2/getUserDetails"
    headers = {"Authorization": "Bearer <token>"}
    params = {}
    response = requests.get(url, headers=headers, params=params)

    # Assertions
    assert response.status_code in [200, 200, 201], f'Expected 200/200/201, got {response.status_code}'
    assert "{'username': 'user123', 'email': 'test@example.com'}" in response.text, 'Expected response to contain "{'username': 'user123', 'email': 'test@example.com'}"'
