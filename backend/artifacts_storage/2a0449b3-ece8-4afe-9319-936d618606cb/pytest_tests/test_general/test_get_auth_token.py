import pytest
import requests

def test_get_auth_token(base_url):
    url = f"{base_url}/getAuthToken"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    params = {}
    payload = {"login.username": "invoice2", "login.password": "vst123", "tenantId": "suprabhat-latest"}
    response = requests.post(url, headers=headers, params=params, data=payload)

    # Assertions
    print(f'Status Code: {response.status_code}')
    print(f'Response Body: {response.text}')
    assert response.status_code in [200, 200, 201]
    # Skipped body text assertion due to placeholder '{'token': '<authToken>'}'

if __name__ == "__main__":
    # Allow running this file directly with Python
    import sys
    sys.exit(pytest.main(["-v", "-s", __file__]))
