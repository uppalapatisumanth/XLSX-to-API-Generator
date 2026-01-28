import pytest
import requests

def test_getsuppliers(base_url):
    url = f"{base_url}/rest/suprabhat/V2/getSuppliers"
    headers = {}
    params = {}
    response = requests.get(url, headers=headers, params=params)

    assert response.status_code == 200, f'Expected 200, got {response.status_code}'
