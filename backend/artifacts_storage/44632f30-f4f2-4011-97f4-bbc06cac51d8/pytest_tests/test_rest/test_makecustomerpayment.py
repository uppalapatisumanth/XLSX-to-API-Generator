import pytest
import requests

def test_makecustomerpayment(base_url):
    url = f"{base_url}/rest/suprabhat/V2/makeCustomerPayment"
    headers = {}
    params = {}
    response = requests.post(url, headers=headers, params=params)

    assert response.status_code == 200, f'Expected 200, got {response.status_code}'
