import pytest
import requests

def test_get_customer_profile_details(base_url, auth_token):
    url = f"{base_url}/getCustomerProfileDetails"
    headers = {
        "token": auth_token,
    }
    params = {
        "Key": "",
        "tenantId": "suprabhat-latest",
        "customerId": "20955",
        "supplierId": "HERITAGE",
        "facilityId": "20955",
    }
    response = requests.get(url, headers=headers, params=params)

    # Assertions
    assert response.status_code in [200, 200, 201]
    # Skipped assertion for empty/None response
