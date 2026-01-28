import pandas as pd

import pandas as pd
import json

# Sheet 1: APIs
# Demonstrating:
# 1. POST Auth with x-www-form-urlencoded body and token extraction
# 2. GET API using the extracted token in a header
# 3. GET API using query params
apis_data = [
    {
        "Ref ID": "AUTH-01",
        "Module/Feature": "Authentication",
        "API Name": "Get Auth Token",
        "HTTP Method": "POST",
        "Endpoint URL": "getAuthToken", # Will be combined with {{base_url}}
        "Headers Required": "Content-Type: application/x-www-form-urlencoded",
        "Request Payload (JSON example)": json.dumps({
            "login.username": "demo_user",
            "login.password": "secret123",
            "tenantId": "demo-tenant"
        }),
        "Expected Response (Success)": '{"token": "<authToken>"}',
        "Token Variable": "authToken",
        "Is Token Generator": "TRUE",
        "Auth Scope": ""
    },
    {
        "Ref ID": "USER-01",
        "Module/Feature": "Users",
        "API Name": "Get Profile",
        "HTTP Method": "GET",
        "Endpoint URL": "getCustomerProfileDetails",
        "Headers Required": "token: {{authToken}}", # Uses the variable from above
        "Request Payload (JSON example)": "",
        "URL Params": json.dumps({
            "customerId": "20955",
            "fullDetails": "true"
        }),
        "Expected Response (Success)": '{"id": 20955}',
        "Token Variable": "",
        "Is Token Generator": "FALSE",
        "Auth Scope": ""
    }
]

# Sheet 2: Environments
# Demonstrating:
# 1. Base URL variable
# 2. Other variables
env_data = [
    {"Variable": "base_url", "Value": "https://api.example.com/v2"},
    {"Variable": "tenantId", "Value": "demo-tenant"}
]

# Write to Excel
file_name = "sample_api.xlsx"
with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
    pd.DataFrame(apis_data).to_excel(writer, sheet_name='apis', index=False)
    pd.DataFrame(env_data).to_excel(writer, sheet_name='environments', index=False)
    
    # Optional: Add formatting or comments here if needed in future
    
print(f"Created {file_name} with 'apis' and 'environments' sheets.")
