import pytest
import requests

def test_getreceiptsandpayments(base_url):
    url = f"{base_url}/rest/suprabhat/V2/getReceiptsAndPayments"
    headers = {}
    params = {}
    response = requests.get(url, headers=headers, params=params)

    assert response.status_code == 200, f'Expected 200, got {response.status_code}'
