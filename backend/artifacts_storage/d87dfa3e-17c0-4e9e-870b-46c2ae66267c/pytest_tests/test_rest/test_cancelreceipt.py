import pytest
import requests

def test_cancelreceipt(base_url):
    url = f"{base_url}/rest/suprabhat/V2/cancelReceipt"
    headers = {}
    params = {}
    response = requests.post(url, headers=headers, params=params)

    assert response.status_code == 200, f'Expected 200, got {response.status_code}'
