import pytest
import requests

def test_get_customer_profile_details(base_url):
    url = f"{base_url}/getCustomerProfileDetails"
    headers = {"token": "{{authToken}}"}
    params = {"Key": "", "tenantId": "suprabhat-latest", "customerId": "20955", "supplierId": "HERITAGE", "facilityId": "20955"}
    response = requests.get(url, headers=headers, params=params)

    # Assertions
    assert response.status_code in [200, 200, 201], f'Expected 200/200/201, got {response.status_code}'
    assert "None" in response.text, """Expected response to contain "None""""
