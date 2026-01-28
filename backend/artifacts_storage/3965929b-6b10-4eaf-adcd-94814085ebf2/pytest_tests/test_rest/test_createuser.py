import pytest
import requests

def test_createuser(base_url, auth_token):
    url = f"{base_url}/rest/suprabhat/V2/createUser"
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    params = {}
    json_body = {"username": "newuser", "role": "admin"}
    response = requests.post(url, headers=headers, params=params, json=json_body)

    # Assertions
    assert response.status_code in [200, 200, 201], f'Expected 200/200/201, got {response.status_code}'
    assert "{'id': 101, 'status': 'created'}" in response.text, """Expected response to contain "{'id': 101, 'status': 'created'}""""
