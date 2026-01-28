import pytest
import requests

def test_getauthtoken(base_url):
    url = f"{base_url}/rest/suprabhat/V2/getAuthToken"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    params = {}
    payload = {"login.username": "user123", "login.password": "pass123", "tenantId": "test-tenant"}
    response = requests.post(url, headers=headers, params=params, data=payload)

    # Assertions
    assert response.status_code in [200, 200, 201], f'Expected 200/200/201, got {response.status_code}'
    assert "{'token': '<JWT_TOKEN>', 'responseMessage': 'success'}" in response.text, 'Expected response to contain "{'token': '<JWT_TOKEN>', 'responseMessage': 'success'}"'
