import sys
import traceback

def log_error(e):
    with open("verify_result.txt", "w") as f:
        f.write(f"STARTUP ERROR: {e}\n")
        traceback.print_exc(file=f)

try:
    import pandas as pd
    import json
    import io
    # Try importing services
    import services.parser as parser
    import services.postman_generator as generator
except Exception as e:
    log_error(e)
    sys.exit(1)

def log(msg, file):
    file.write(str(msg) + "\n")
    print(msg)

def test_full_flow():
    with open("verify_result.txt", "w") as f:
        log("--- 1. Creating Test Excel ---", f)
        
        # Check if xlsxwriter is available for pandas
        try:
           import xlsxwriter
        except ImportError:
           log("CRITICAL: xlsxwriter not found. Cannot create test excel.", f)
           return
        
        # 1. APIs Sheet
        apis_data = [
            {
                "Ref ID": "TEST-01",
                "Module/Feature": "TestModule",
                "API Name": "Test Get",
                "HTTP Method": "GET",
                "Endpoint URL": "test/get",
                "Headers Required": "Content-Type: application/json",
                "Request Payload (JSON example)": "",
                "Expected Response (Success)": "{}"
            }
        ]
        
        # 2. Environments Sheet (New Feature)
        env_data = [
            {"Variable": "base_url", "Value": "https://api.test.com"},
            {"Variable": "tenantId", "Value": "test-tenant"},
            {"Variable": "customerId", "Value": "12345"}
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
        
        log("Parsed Env: " + json.dumps(parsed_data.get("env"), indent=2), f)
        
        # Validation
        env = parsed_data.get("env", {})
        if env.get("base_url") != "https://api.test.com":
            log("FAILURE: base_url not parsed correctly", f)
            return
        if env.get("tenantId") != "test-tenant":
            log("FAILURE: tenantId not parsed correctly", f)
            return
            
        log("SUCCESS: Parser worked.", f)
        
        log("\n--- 3. Testing Generator ---", f)
        collection = generator.generate_postman_collection(parsed_data, "Test Collection")
        
        # Validate Collection Variables
        vars = {v['key']: v['value'] for v in collection.get('variable', [])}
        log("Collection Vars: " + json.dumps(vars, indent=2), f)
        
        if "base_url" not in vars or vars["base_url"] != "https://api.test.com":
            log("FAILURE: base_url missing in collection variables", f)
            return
            
        # Validate Request URL
        item = collection['item'][0]['item'][0] # Module -> Request
        url_raw = item['request']['url']['raw']
        log(f"Generated URL: {url_raw}", f)
        
        if "{{base_url}}" not in url_raw:
            log(f"FAILURE: URL does not contain {{{{base_url}}}}. Found: {url_raw}", f)
            return
            
        log("SUCCESS: Generator worked.", f)

if __name__ == "__main__":
    try:
        test_full_flow()
    except Exception as e:
        with open("verify_result.txt", "a") as f:
            f.write(f"CRITICAL ERROR: {e}\n")

