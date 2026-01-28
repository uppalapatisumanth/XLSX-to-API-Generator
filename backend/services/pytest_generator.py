import os
import shutil
import zipfile
import json
from pathlib import Path

def generate_pytest_project(api_data, output_dir: str):
    """
    Generates a Pytest project structure from API data.
    api_data can be either:
    - A dict with {"apis": [...], "env": {}, "rules": {}}
    - Or a list of API dicts directly (legacy)
    """
    
    # Handle both dict format and list format
    if isinstance(api_data, dict):
        apis = api_data.get("apis", [])
    elif isinstance(api_data, list):
        apis = api_data
    else:
        apis = []
    
    base_dir = Path(output_dir)
    tests_dir = base_dir / "pytest_tests"
    if tests_dir.exists():
        shutil.rmtree(tests_dir)
    tests_dir.mkdir(parents=True)
    
    # Generate requirements.txt
    _create_file(tests_dir / "requirements.txt", "pytest\nrequests\n")
    
    # Extract env from api_data
    env = {}
    if isinstance(api_data, dict):
        env = api_data.get("env", {})
    
    # Generate conftest.py
    _create_conftest(tests_dir, apis, env)
    
    # Group APIs (logic: try to group by first path segment, or 'general')
    groups = {}
    for api in apis:
        # Simple grouping heuristic
        path_parts = api.get("url", "").split("://")[-1].split("/")
        group_name = "general"
        if len(path_parts) > 1 and path_parts[1]:
             group_name = path_parts[1]
        
        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(api)
        
    # Generate Test Files
    for group, apis in groups.items():
        group_dir = tests_dir / f"test_{group}"
        group_dir.mkdir(exist_ok=True)
        # Create __init__.py for the package
        _create_file(group_dir / "__init__.py", "")
        
        for api in apis:
            _create_test_file(group_dir, api)
            
    # Zip the directory
    zip_path = base_dir / "pytest_tests.zip"
    _zip_directory(tests_dir, zip_path)
    
    return str(zip_path)

def _create_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def _create_conftest(base_path, apis, env={}):
    # Find Token Generator API
    token_api = next((api for api in apis if api.get("is_token_generator")), None)
    
    # Determine default base url
    default_base_url = env.get("base_url", "http://localhost:8000")
    
    content = f"""import pytest
import os
import requests
import json

@pytest.fixture(scope="session")
def base_url():
    # Allow overriding via env var, validation could be added here
    return os.getenv("API_BASE_URL", "{default_base_url}")

@pytest.fixture(scope="session")
def auth_token(base_url):
"""

    if token_api:
        # Generate code to call the token API
        url = token_api.get("url", "")
        method = token_api.get("method", "POST").lower()
        headers = token_api.get("headers", {})
        body = token_api.get("body", {})
        url_params = token_api.get("url_params", {})
        token_var = token_api.get("token_variable", "token")
        
        # Path handling code (similar to test file)
        if "://" in url:
            path = "/" + "/".join(url.split("://")[-1].split("/")[1:])
        else:
            path = url if url.startswith("/") else f"/{url}"
            
        content += f"    # Token Generator API: {token_api.get('name')}\n"
        content += f"    url = f'{{base_url}}{path}'\n"
        content += f"    headers = {json.dumps(headers)}\n"
        
        # Determine payload
        # Determine payload
        if method in ['post', 'put', 'patch']:
            if token_api.get("body_mode") == "urlencoded":
                # Use body if present, else params. Requests handles dict->form-data
                payload = body or url_params
                content += f"    data = {json.dumps(payload)}\n"
                content += f"    response = requests.{method}(url, headers=headers, data=data)\n"
            else:
                content += f"    json_body = {json.dumps(body)}\n"
                content += f"    response = requests.{method}(url, headers=headers, json=json_body)\n"
        else:
             content += f"    response = requests.{method}(url, headers=headers)\n"
             
        content += f"    if response.status_code not in [200, 201]:\n"
        content += f"        return None\n"
        content += f"    \n"
        content += f"    data = response.json()\n"
        content += f"    # Try to extract token\n"
        content += f"    token = data.get('{token_var}') or data.get('token') or data.get('access_token')\n"
        content += f"    return token\n"
        
    else:
        content += """    # No Token Generator API found. 
    # Configure via env var if needed.
    return os.getenv("AUTH_TOKEN", None)
"""
    
    _create_file(base_path / "conftest.py", content)

def _create_test_file(directory, api):
    clean_name = api.get("name", "untitled").lower().replace(" ", "_").replace("-", "_")
    filename = f"test_{clean_name}.py"
    
    method = api.get("method", "GET").lower()
    url = api.get("url", "")
    headers = api.get("headers", {})
    body = api.get("body", {})
    params = api.get("params", {})
    expected_response = api.get("expected_response")
    expected_response_type = api.get("expected_response_type", "text")
    status = api.get("status", 200)

    body_mode = api.get("body_mode", "raw")
    is_auth = api.get("is_auth", False)
    
    # Identify token variable to substitute
    # We assume 'authToken' or 'token' is the fixture name
    token_fixture_name = "auth_token"

    # Helper to handle {{variable}} substitution
    import re
    def sanitize(val):
        """Converts {{var}} to string interpolation or direct variable usage."""
        if not isinstance(val, str): return val
        
        # Regex to find {{ var }} with optional whitespace
        match = re.search(r"\{\{\s*(\w+)\s*\}\}", val)
        if match:
            var_name = match.group(1)
            # Normalize auth token name
            if var_name in ["authToken", "token"]:
                if val.strip() == match.group(0): # Entire string is the variable
                    return "___AUTH_TOKEN_PLACEHOLDER___"
                else:
                    return val.replace(match.group(0), "{auth_token}")
        return val

    # Recursively process dicts/lists
    def process_structure(data):
        if isinstance(data, dict):
            return {k: process_structure(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [process_structure(i) for i in data]
        else:
            return sanitize(data)

    headers = process_structure(headers)
    params = process_structure(params)
    body = process_structure(body)

    # 1. URL Handler
    if "://" in url:
        path = "/" + "/".join(url.split("://")[-1].split("/")[1:])
    else:
        path = url if url.startswith("/") else f"/{url}"
    
    # 2. Body Handling
    final_body = body
    use_params_as_body = False
    
    if not final_body and body_mode == "urlencoded" and params:
        final_body = params
        use_params_as_body = True

    # 3. Construct Code
    # Determine needed fixtures
    fixtures = ["base_url"]
    
    # Check if we need auth_token
    needs_auth = False
    # Check headers for placeholder
    if str(headers).find("___AUTH_TOKEN_PLACEHOLDER___") != -1: needs_auth = True
    # Check auth scope
    if str(api.get("auth_scope", "")).lower() == "collection": needs_auth = True
    
    if needs_auth:
        fixtures.append("auth_token")

    code = "import pytest\nimport requests\n\n"
    code += f"def test_{clean_name}({', '.join(fixtures)}):\n"
    code += f"    url = f\"{{base_url}}{path}\"\n"
    
    # Render Headers
    # We construct the dict string manually to handle variables
    if headers:
        code += "    headers = {\n"
        for k, v in headers.items():
            if v == "___AUTH_TOKEN_PLACEHOLDER___":
                code += f"        \"{k}\": {token_fixture_name},\n"
            else:
                code += f"        \"{k}\": \"{v}\",\n"
        code += "    }\n"
    else:
        code += "    headers = {}\n"

    # Explicit Auth Scope Injection (if not already handled by header var)
    if str(api.get("auth_scope", "")).lower() == "collection" and "Authorization" not in headers:
         code += f"    headers['Authorization'] = f'Bearer {{{token_fixture_name}}}'\n"

    # Render Params
    if use_params_as_body:
        code += "    params = {}\n"
    else:
        if params:
            code += "    params = {\n"
            for k, v in params.items():
                code += f"        \"{k}\": \"{v}\",\n"
            code += "    }\n"
        else:
            code += "    params = {}\n"

    # Make Request
    if method in ['post', 'put', 'patch'] and final_body:
        if body_mode == "urlencoded":
            code += f"    payload = {json.dumps(final_body)}\n"
            code += f"    response = requests.{method}(url, headers=headers, params=params, data=payload)\n"
        else:
            code += f"    json_body = {json.dumps(final_body)}\n"
            code += f"    response = requests.{method}(url, headers=headers, params=params, json=json_body)\n"
    else:
        code += f"    response = requests.{method}(url, headers=headers, params=params)\n"

    # Assertions
    code += "\n    # Assertions\n"
    code += "    print(f'Status Code: {response.status_code}')\n"
    code += "    print(f'Response Body: {response.text}')\n"
    code += f"    assert response.status_code in [{status}, 200, 201]\n"

    if expected_response:
        if expected_response_type == "json":
            code += f"    response_json = response.json()\n"
            for k, v in expected_response.items():
                if isinstance(v, str):
                   # Placeholder check
                   if "<" in v and ">" in v:
                       code += f"    # Skipped assertion for {k} due to placeholder '{v}'\n"
                   else:
                       code += f"    assert response_json.get('{k}') == \"{v}\"\n"
                else:
                    code += f"    assert response_json.get('{k}') == {v}\n"
        else:
            # Plain String Assertion
            safe_str = str(expected_response).replace('"', '\\"')
            if safe_str == "None" or safe_str == "":
                 code += f"    # Skipped assertion for empty/None response\n"
            elif "<" in safe_str and ">" in safe_str:
                code += f"    # Skipped body text assertion due to placeholder '{safe_str}'\n"
            else:
                code += f"    assert \"{safe_str}\" in response.text\n"

    
    # 5. Local Execution Block
    code += "\nif __name__ == \"__main__\":\n"
    code += "    # Allow running this file directly with Python\n"
    code += "    import sys\n"
    code += "    sys.exit(pytest.main([\"-v\", \"-s\", __file__]))\n"

    _create_file(directory / filename, code)

def _zip_directory(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(folder_path)
                zipf.write(file_path, arcname)
