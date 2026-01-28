import pytest
import requests

def test_createuser(base_url):
    url = f"{base_url}/rest/suprabhat/V2/createUser"
    headers = {
        "Content-Type": "application/json",
    }
    params = {}
    json_body = {"username": "newuser", "role": "admin"}
    response = requests.post(url, headers=headers, params=params, json=json_body)

    # Assertions
    print(f'Status Code: {response.status_code}')
    print(f'Response Body: {response.text}')
    assert response.status_code in [200, 200, 201]
    assert "{'id': 101, 'status': 'created'}" in response.text

if __name__ == "__main__":
    # Allow running this file directly with Python
    import sys
    sys.exit(pytest.main(["-v", "-s", __file__]))
