
import pandas as pd
import json
import io
import sys
import traceback

def log(msg, file):
    file.write(str(msg) + "\n")
    print(msg)

def log_error(e):
    with open("verify_auth_result.txt", "w") as f:
        f.write(f"STARTUP ERROR: {e}\n")
        traceback.print_exc(file=f)

try:
    import services.parser as parser
    import services.postman_generator as generator
except Exception as e:
    log_error(e)
    sys.exit(1)

def test_auth_flow():
    with open("verify_auth_result.txt", "w") as f:
        log("--- 1. Creating Auth Flow Excel ---", f)
        
        # 1. APIs Sheet
        # Scenario: 
        # API 1: getAuthToken (POST) -> Extracts 'token' to {{authToken}}
        # API 2: getProfile (GET) -> Uses header 'token': '{{authToken}}'
        
        apis_data = [
            {
                "Ref ID": "AUTH-01",
                "Module/Feature": "Auth",
                "API Name": "getAuthToken",
                "HTTP Method": "POST",
                "Endpoint URL": "getAuthToken",
                "Headers Required": "Content-Type: application/json",
                "Request Payload (JSON example)": "{}",
                "Expected Response (Success)": "{\"token\": \"<authToken>\"}", 
                "Token Variable": "authToken",
                "Is Token Generator": "TRUE"
            },
            {
                "Ref ID": "DATA-01",
                "Module/Feature": "Data",
                "API Name": "Get Customer Profile",
                "HTTP Method": "GET",
                "Endpoint URL": "getCustomerProfileDetails",
                "Headers Required": "token: {{authToken}}",
                "Request Payload (JSON example)": "",
                "Expected Response (Success)": "{}"
            }
        ]
        
        # 2. Environments Sheet
        env_data = [
            {"Variable": "base_url", "Value": "https://master.suprabhatapp.in/rest/suprabhat/V2"},
            {"Variable": "tenantId", "Value": "suprabhat-latest"}
        ]
        
        # Create BytesIO buffer
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(apis_data).to_excel(writer, sheet_name='apis', index=False)
            pd.DataFrame(env_data).to_excel(writer, sheet_name='environments', index=False)
        
        excel_bytes = output.getvalue()
        log(f"Excel created in memory, size: {len(excel_bytes)}", f)
        
        log("\n--- 2. Testing Parser ---", f)
        parsed_data, warnings = parser.parse_xlsx(excel_bytes)
        
        if warnings:
            log(f"Warnings: {warnings}", f)
            
        # Check if 'token' header was parsed correctly for the second API
        api2 = parsed_data['apis'][1]
        log(f"API 2 Headers: {api2['headers']}", f)
        
        if api2['headers'].get('token') != '{{authToken}}':
             log(f"FAILURE: Parser did not preserve 'token' header value. Got: {api2['headers'].get('token')}", f)
             return

        log("SUCCESS: Parser handled custom header variable.", f)
        
        log("\n--- 3. Testing Generator ---", f)
        collection = generator.generate_postman_collection(parsed_data, "Auth Test Collection")
        
        # Check API 1: Token Generation Script
        item1 = collection['item'][0]['item'][0]
        event1 = item1.get('event', [])
        test_script = ""
        for e in event1:
            if e['listen'] == 'test':
                 test_script = "\n".join(e['script']['exec'])
        
        log(f"API 1 Test Script:\n{test_script}", f)
        
        if "authToken" not in test_script:
            log("FAILURE: Generator did not create script for 'authToken'", f)
            return
            
        # Check API 2: Header usage
        item2 = collection['item'][1]['item'][0] # separate folder 'Data'
        headers2 = item2['request']['header']
        
        log(f"API 2 Postman Headers: {json.dumps(headers2, indent=2)}", f)
        
        found_token_header = False
        for h in headers2:
            if h['key'] == 'token' and h['value'] == '{{authToken}}':
                found_token_header = True
                break
        
        if not found_token_header:
            log("FAILURE: Postman Request does not have correct 'token' header.", f)
            return

        log("SUCCESS: Generator handled custom header flow.", f)

if __name__ == "__main__":
    try:
        test_auth_flow()
    except Exception as e:
        with open("verify_auth_result.txt", "a") as f:
             f.write(f"CRITICAL ERROR: {e}\n")
             traceback.print_exc(file=f)
