import pytest
import requests

def test_getuserdetails(base_url):
    url = f"{base_url}/rest/suprabhat/V2/getUserDetails"
    headers = {
        "Authorization": "Bearer <token>",
    }
    params = {}
    response = requests.get(url, headers=headers, params=params)

    # Assertions
    print(f'Status Code: {response.status_code}')
    print(f'Response Body: {response.text}')
    assert response.status_code in [200, 200, 201]
    assert "{'username': 'user123', 'email': 'test@example.com'}" in response.text

if __name__ == "__main__":
    # Allow running this file directly with Python
    import sys
    sys.exit(pytest.main(["-v", "-s", __file__]))
