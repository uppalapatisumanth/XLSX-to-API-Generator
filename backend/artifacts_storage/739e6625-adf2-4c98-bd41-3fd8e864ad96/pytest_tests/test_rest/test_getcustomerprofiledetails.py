import pytest
import requests

def test_getcustomerprofiledetails(base_url, auth_token):
    url = f"{base_url}/rest/suprabhat/V2/getCustomerProfileDetails?tenantId=suprabhat-latest&customerId=20955&supplierId=HERITAGE&facilityId=20955"
    headers = {"token": "suprabhat-latest"}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    params = {}
    response = requests.get(url, headers=headers, params=params)

    # Assertions
    assert response.status_code in [200, 200, 201], f'Expected 200/200/201, got {response.status_code}'
    assert "None" in response.text, """Expected response to contain "None""""
