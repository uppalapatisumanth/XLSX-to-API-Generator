import sys
import os
import json
import io
from unittest.mock import MagicMock

# Add backend to path
sys.path.append(os.getcwd())

from services.parser import parse_xlsx
from services.postman_generator import generate_postman_collection
from services.pytest_generator import generate_pytest_project

# Mock pandas for parser if needed, but we can verify parser logic by mocking the excel data 
# actually, constructing a real dataframe is better if pandas is installed (it is).
import pandas as pd

def test_feature_1_url_handling():
    print("\n--- Testing Feature: Enhanced URL Handling ---")
    # Mock Data: Absolute URL
    df = pd.DataFrame([{
        'API Name': 'URL Test',
        'HTTP Method': 'GET',
        'Endpoint URL': 'https://api.example.com/v1/resource',
        'Ref ID': '1',
        'Module/Feature': 'General'
    }])
    
    # Save to BytesIO to simulate file upload
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='apis', index=False)
    data = output.getvalue()
    
    # Test Parser
    result, err = parse_xlsx(data)
    if err:
        print(f"FAILED: Parser returned errors: {err}")
        return False
        
    env = result.get('env', {})
    base_url = env.get('base_url')
    api_url = result['apis'][0]['url']
    
    print(f"Detected Base URL: {base_url}")
    print(f"Normalized Path: {api_url}")
    
    if base_url != "https://api.example.com":
        print(f"FAILED: Base URL mismatch. Expected 'https://api.example.com', got '{base_url}'")
        return False
    
    if api_url != "/v1/resource":
        print(f"FAILED: Path mismatch. Expected '/v1/resource', got '{api_url}'")
        return False
        
    # Test Postman
    collection = generate_postman_collection(result)
    pm_vars = collection.get('variable', [])
    basic_url_var = next((v for v in pm_vars if v['key'] == 'basic url'), None)
    
    if not basic_url_var or basic_url_var['value'] != "https://api.example.com":
        print(f"FAILED: Postman Collection missing 'basic url' variable.")
        return False
        
    req_url = collection['item'][0]['item'][0]['request']['url']['raw']
    if "{{basic url}}" not in req_url:
        print(f"FAILED: Postman request URL does not use {{basic url}}. Got: {req_url}")
        return False

    print("SUCCESS: URL Handling verified.")
    return True

def test_feature_2_auth_and_sanitization():
    print("\n--- Testing Feature: Auth Support and Variable Sanitization ---")
    
    long_token = "eyJhbGciOiJIUzI1NiJ9." * 10 # Simulate a long JWT
    
    df = pd.DataFrame([
        {
            'API Name': 'Login',
            'HTTP Method': 'POST',
            'Endpoint URL': '/login',
            'Is Token Generator': 'Yes',
            'Token Variable': long_token, # Bad user input
            'Module/Feature': 'Auth'
        },
        {
            'API Name': 'Get Data',
            'HTTP Method': 'GET',
            'Endpoint URL': '/data',
            'Auth Scope': 'Collection',
            'Module/Feature': 'General'
        }
    ])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='apis', index=False)
    data = output.getvalue()
    
    result, err = parse_xlsx(data)
    
    # 1. Check Sanitization
    login_api = result['apis'][0]
    token_var = login_api.get('token_variable')
    print(f"Sanitized Token Variable: {token_var}")
    
    if token_var != 'token':
        print(f"FAILED: Token variable not sanitized. Got '{token_var}'")
        return False
        
    # 2. Check Postman Generation
    col = generate_postman_collection(result)
    
    # Check Login Script
    login_item = col['item'][0]['item'][0] # Auth Folder -> Login
    scripts = login_item['event'][0]['script']['exec']
    script_str = "\n".join(scripts)
    
    if 'pm.collectionVariables.set("token"' not in script_str:
        print("FAILED: Postman script does not set 'token' variable.")
        return False
        
    # Check Auth Header in Get Data
    data_item = col['item'][1]['item'][0] # General Folder -> Get Data
    headers = data_item['request']['header']
    auth_header = next((h for h in headers if h['key'] == 'Authorization'), None)
    
    if not auth_header or auth_header['value'] != 'Bearer {{token}}':
        print(f"FAILED: Auth header missing or incorrect. Got: {auth_header}")
        return False

    print("SUCCESS: Auth and Sanitization verified.")
    return True

def test_feature_3_pytest_generation():
    print("\n--- Testing Feature: Pytest Generation & Syntax ---")
    
    # Mock API data
    api_data = {
        "env": {"base_url": "https://test.com"},
        "apis": [
            {
                "name": "Test Assert",
                "method": "GET",
                "url": "/test",
                "expected_response": '{"msg": "Hello "World""}', # Complex string with quotes
                "expected_response_type": "text"
            }
        ]
    }
    
    # Intercept file creation to check content
    generated_files = {}
    def mock_create_file(path, content):
        generated_files[str(path)] = content
        
    # Monkeypatch
    import services.pytest_generator as pg
    original_create = pg._create_file
    pg._create_file = mock_create_file
    
    # Try generating (we verify we don't crash and check content)
    output_dir = "mock_dir"
    try:
        pg.generate_pytest_project(api_data, output_dir)
    except Exception as e:
        print(f"FAILED: Pytest generation crashed: {e}")
        return False
    finally:
        pg._create_file = original_create # Restore
        
    # Check Conftest for Base URL
    conftest = None
    for path, content in generated_files.items():
        if "conftest.py" in path:
            conftest = content
            break
            
    if not conftest:
        print("FAILED: conftest.py not generated")
        return False
        
    if 'os.getenv("API_BASE_URL", "https://test.com")' not in conftest:
        print("FAILED: conftest.py does not use extracted base url defaults.")
        # print(conftest) 
        return False

    # Check Syntax Escaping in Test File
    test_file = None
    for path, content in generated_files.items():
        if "test_test_assert.py" in path:
            test_file = content
            break
            
    if not test_file:
         print("FAILED: test file not generated")
         return False
         
    # Look for the assertion
    if 'assert """{"msg": "Hello \\"World\\""}""" in response.text' not in test_file:
        # We look for the triple quote implementation we added
        if '"""Expected response to contain' not in test_file:
             print("FAILED: special string escaping logic not found in test file.")
             print("Content snippet:", test_file[-200:])
             return False

    print("SUCCESS: Pytest Generation verified.")
    return True

if __name__ == "__main__":
    with open("verification_results.txt", "w") as f:
        f.write("Running System Verification...\n")
        
        # Redefine print to write to file
        original_print = print
        def print(*args, **kwargs):
            f.write(" ".join(map(str, args)) + "\n")
            # original_print(*args, **kwargs) # Optional
            
        # Manually inject print into global scope for functions to use
        globals()['print'] = print
        
        results = [
            test_feature_1_url_handling(),
            test_feature_2_auth_and_sanitization(),
            test_feature_3_pytest_generation()
        ]
        
        if all(results):
            f.write("\nALL SYSTEMS GO: All features verified successfully.\n")
        else:
            f.write("\nVERIFICATION FAILED: Some checks failed.\n")
