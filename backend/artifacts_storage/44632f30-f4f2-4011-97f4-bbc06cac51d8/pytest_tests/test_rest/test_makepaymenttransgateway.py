import pytest
import requests

def test_makepaymenttransgateway(base_url):
    url = f"{base_url}/rest/suprabhat/V2/makePaymentTransGateway"
    headers = {}
    params = {}
    response = requests.post(url, headers=headers, params=params)

    assert response.status_code == 200, f'Expected 200, got {response.status_code}'
