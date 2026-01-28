import pytest
import requests

def test_getauthtoken(base_url):
    url = f"{base_url}/rest/suprabhat/V2/getAuthToken"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    params = {
        "login.username": "user123",
        "login.password": "pass123",
        "tenantId": "test-tenant",
    }
    payload = {"login.username": "user123", "login.password": "pass123", "tenantId": "test-tenant"}
    response = requests.post(url, headers=headers, params=params, data=payload)

    # Assertions
    print(f'Status Code: {response.status_code}')
    print(f'Response Body: {response.text}')
    assert response.status_code in [200, 200, 201]
    # Skipped body text assertion due to placeholder '{'token': '<JWT_TOKEN>', 'responseMessage': 'success'}'

if __name__ == "__main__":
    # Allow running this file directly with Python
    import sys
    sys.exit(pytest.main(["-v", "-s", __file__]))
