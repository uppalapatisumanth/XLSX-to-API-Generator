import pandas as pd
import json
import io
import sys
import traceback

def log(msg, file):
    file.write(str(msg) + "\n")
    print(msg)

def log_error(e):
    with open("verify_post_result.txt", "w") as f:
        f.write(f"STARTUP ERROR: {e}\n")
        traceback.print_exc(file=f)

try:
    import services.parser as parser
    import services.postman_generator as generator
except Exception as e:
    log_error(e)
    sys.exit(1)

def test_post_flow():
    with open("verify_post_result.txt", "w") as f:
        log("--- 1. Creating POST Auth Excel ---", f)
        
        # Scenario from Screenshot:
        # POST {{baseURL}}/rest/suprabhat/V2/getAuthToken
        # Body: x-www-form-urlencoded
        #   login.username: invoice2
        #   login.password: vst123
        #   tenantId: suprabhat-latest
        # Script: extract token to authToken
        
        apis_data = [
            {
                "Ref ID": "AUTH-02",
                "Module/Feature": "Auth",
                "API Name": "getAuthToken",
                "HTTP Method": "POST",
                "Endpoint URL": "getAuthToken",
                "Headers Required": "Content-Type: application/x-www-form-urlencoded", # Critical for triggering mode
                "Request Payload (JSON example)": json.dumps({
                    "login.username": "invoice2",
                    "login.password": "vst123",
                    "tenantId": "suprabhat-latest"
                }),
                "Expected Response (Success)": "{\"token\": \"<authToken>\"}", 
                "Token Variable": "authToken",
                "Is Token Generator": "TRUE"
            }
        ]
        
        # Environments Sheet - User used camelCase {{baseURL}} in screenshot
        env_data = [
            {"Variable": "baseURL", "Value": "https://master.suprabhatapp.in"}
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
        if warnings: log(f"Warnings: {warnings}", f)
        
        api = parsed_data['apis'][0]
        log(f"Parsed Body Mode: {api.get('body_mode')}", f)
        
        if api.get('body_mode') != 'urlencoded':
             log("FAILURE: body_mode should be 'urlencoded' due to Content-Type header.", f)
             return

        # Check Environment Base Var Detection
        log(f"Parsed Env: {parsed_data.get('env')}", f)
        
        log("\n--- 3. Testing Generator ---", f)
        collection = generator.generate_postman_collection(parsed_data, "POST Auth Test")
        
        item = collection['item'][0]['item'][0]
        request = item['request']
        
        # Check URL Variable (Should match baseURL from env)
        url_raw = request['url']['raw']
        log(f"Generated URL: {url_raw}", f)
        if "{{baseURL}}" not in url_raw:
             log(f"FAILURE: URL did not use {{baseURL}}. Got: {url_raw}. (Note: variable matching logic might need update)", f)
             return

        # Check Body
        body = request['body']
        log(f"Body Mode: {body.get('mode')}", f)
        log(f"Body Content: {json.dumps(body.get('urlencoded'), indent=2)}", f)
        
        if body.get('mode') != 'urlencoded':
             log("FAILURE: Postman body mode is not urlencoded", f)
             return
             
        # Verify Keys
        keys = [x['key'] for x in body['urlencoded']]
        if "login.username" not in keys:
             log("FAILURE: login.username key missing from body", f)
             return
             
        # Check Script
        event = item.get('event', [])
        test_script = ""
        for e in event:
            if e['listen'] == 'test':
                 test_script = "\n".join(e['script']['exec'])
        
        log(f"Test Script:\n{test_script}", f)
        
        if "authToken" not in test_script or "jsonData.token" not in test_script:
             log("FAILURE: Script properly extracting authToken not found", f)
             return
             
        log("SUCCESS: POST Auth flow verified.", f)

if __name__ == "__main__":
    try:
        test_post_flow()
    except Exception as e:
        with open("verify_post_result.txt", "a") as f:
             f.write(f"CRITICAL ERROR: {e}\n")
             traceback.print_exc(file=f)
