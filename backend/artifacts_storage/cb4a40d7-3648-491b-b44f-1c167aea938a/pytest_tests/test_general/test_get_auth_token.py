import pytest
import requests

def test_get_auth_token(base_url):
    url = f"{base_url}/getAuthToken"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    params = {}
    json_body = {"login.username": "invoice2", "login.password": "vst123", "tenantId": "suprabhat-latest"}
    response = requests.post(url, headers=headers, params=params, json=json_body)

    # Assertions
    assert response.status_code in [200, 200, 201], f'Expected 200/200/201, got {response.status_code}'
    assert "{'token': '<authToken>'}" in response.text, """Expected response to contain "{'token': '<authToken>'}""""
