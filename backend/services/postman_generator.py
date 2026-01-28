import json
import urllib.parse

def generate_postman_collection(api_data, collection_name="Generated Collection") -> dict:
    """
    Generates a Postman Collection v2.1 JSON from parsed API data.
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
    
    collection_id = str(hash(collection_name)) # Simple ID generation
    
    # Determine Environment Variables & Base URL Variable
    env_vars = {}
    base_url_variable = "basic url" # Default
    
    if isinstance(api_data, dict) and "env" in api_data:
        env_vars = api_data["env"]
        # Heuristic for base url variable
        candidates = ['base_url', 'baseUrl', 'host', 'basic url']
        for c in candidates:
             if c in env_vars:
                 base_url_variable = c
                 break

    collection = {
        "info": {
            "_postman_id": collection_id,
            "name": collection_name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "variable": []
    }
    
    # Add Env Vars to Collection
    for k, v in env_vars.items():
        collection["variable"].append({
            "key": k,
            "value": v,
            "type": "string"
        })
    
    folder_map = {}
    
    for api in apis:
        request_item = _create_postman_request(api, base_url_variable)
        module = api.get("module", "General")
        
        if module not in folder_map:
            folder_map[module] = {
                "name": module,
                "item": []
            }
        folder_map[module]["item"].append(request_item)
        
    # Convert folder map to list
    for module_name, folder in folder_map.items():
        collection["item"].append(folder)

    return collection

def _create_postman_request(api, base_url_variable="basic url"):
    """
    Creates a single Postman request item.
    """
    # Parse URL to separate base generic parts (handled by env vars ideally, but here we keep it simple or use variable)
    # For this simplified version, we just put the full URL. 
    
    url_str = api.get("url", "")
    method = api.get("method", "GET")
    name = api.get("name", "Untitled API")
    headers = api.get("headers", {})
    body = api.get("body", {})
    params = api.get("params", {})
    expected_response = api.get("expected_response")
    expected_response_type = api.get("expected_response_type", "text")
    status = api.get("status", 200)
    body_mode = api.get("body_mode", "json")
    
    # Auto-detect body mode from headers
    if headers:
        for k, v in headers.items():
            if k.lower() == "content-type" and "x-www-form-urlencoded" in str(v).lower():
                body_mode = "urlencoded"
                break

    is_auth = api.get("is_auth", False)
    if not is_auth and ("auth" in name.lower() or "login" in name.lower() or "token" in name.lower()):
        is_auth = True

    auth_scope = api.get("auth_scope", "")
    token_var = api.get("token_variable", "token")
    is_token_gen = api.get("is_token_generator", False)

    auth_scope = api.get("auth_scope", "")
    token_var = api.get("token_variable", "token")
    is_token_gen = api.get("is_token_generator", False)

    # 1. URL Handler: Custom variable {{basic url}}
    # Parser now ensures 'url' is relative path if absolute was provided
    # But we check just in case or if "://" remains
    path = url_str
    if "://" in url_str:
         path = "/" + "/".join(url_str.split("://")[-1].split("/")[1:])
    else:
         if not url_str.startswith("/"):
             path = f"/{url_str}"

    # Requirement: Match user's "actual output" variable style
    final_url = f"{{{{{base_url_variable}}}}}" + path
    
    pm_url = {
        "raw": final_url,
        "host": [f"{{{{{base_url_variable}}}}}"],
        "path": path.strip("/").split("/"),
        "query": []
    }

    # Construct the Request Object
    pm_request = {
        "method": method,
        "header": [],
        "url": pm_url,
        "description": f"Request for {name}"
    }

    # 2. Headers Handler
    if body and "Content-Type" not in headers:
         headers["Content-Type"] = "application/json"

    # Apply Collection Auth if requested
    if str(auth_scope).lower() == "collection":
        pm_request["header"].append({
            "key": "Authorization",
            "value": f"Bearer {{{{{token_var}}}}}",
            "type": "text"
        })

    if isinstance(headers, dict):
        for k, v in headers.items():
            pm_request["header"].append({
                "key": k,
                "value": str(v),
                "type": "text"
            })
            
    # 3. Body Handler
    final_body = body
    use_params_as_body = False
    
    # Fallback: If body is empty, mode is urlencoded, and params exist (from "URL Params" col)
    # Use params as the body
    if not final_body and body_mode == "urlencoded" and params:
        final_body = params
        use_params_as_body = True
    
    if final_body:
        if body_mode == "urlencoded":
            # Convert dict to Postman urlencoded list
            urlencoded_data = []
            if isinstance(final_body, dict):
                for k, v in final_body.items():
                    urlencoded_data.append({
                        "key": k,
                        "value": str(v),
                        "type": "text"
                    })
            
            pm_request["body"] = {
                "mode": "urlencoded",
                "urlencoded": urlencoded_data
            }
        else:
            # Default to raw JSON
            pm_request["body"] = {
                "mode": "raw",
                "raw": json.dumps(final_body, indent=4),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            }

    # Query Params (Only if NOT used as body)
    if isinstance(params, dict) and not use_params_as_body:
        for k, v in params.items():
            pm_request["url"]["query"].append({
                "key": k,
                "value": str(v)
            })

    # 4. Assertions & Extraction Handler
    exec_script = [
        "pm.test(\"Successful request\", function () {",
        f"    pm.expect(pm.response.code).to.be.oneOf([{status}, 200, 201]);",
        "});"
    ]
    
    # Explicit Token Generator Logic
    if is_token_gen:
        exec_script.append(f"// Token Generator for variable: {token_var}")
        exec_script.append("var jsonData = pm.response.json();")
        
        # User Requirement: Use pm.globals.set() as per screenshots (globals scope is preferred by user)
        # We try to find the exact variable name first, then fallback to common 'token' names
        exec_script.append(f"if (jsonData.{token_var}) {{ pm.globals.set(\"{token_var}\", jsonData.{token_var}); }}")
        exec_script.append(f"else if (jsonData.token) {{ pm.globals.set(\"{token_var}\", jsonData.token); }}")
        exec_script.append(f"else if (jsonData.access_token) {{ pm.globals.set(\"{token_var}\", jsonData.access_token); }}")

    # Legacy Auto-Auth Extraction (Heuristic) - only if not explicit
    elif is_auth:
        exec_script.append("// Auto-detected Authentication API")
        exec_script.append("var jsonData = pm.response.json();")
        exec_script.append("if (jsonData.token) { pm.globals.set(\"token\", jsonData.token); }")
        exec_script.append("if (jsonData.access_token) { pm.globals.set(\"token\", jsonData.access_token); }")

    if expected_response:
        if expected_response_type == "json":
            if not is_auth: # Don't redeclare jsonData if we did it for auth
                exec_script.append("var jsonData = pm.response.json();")
            
            # Auto-Extraction Logic: Look for placeholders like <token> or <JWT_TOKEN>
            # And generate pm.globals.set()
            for k, v in expected_response.items():
                if isinstance(v, str):
                    # Check for extraction indicators (<...>)
                    if v.startswith("<") and v.endswith(">"):
                        var_name = k # Use the key as the variable name
                        exec_script.append(f"pm.globals.set(\"{var_name}\", jsonData.{k});")
                    else:
                        # Standard Assertion
                        val_repr = json.dumps(v)
                        exec_script.append(f"pm.test(\"Check {k}\", function () {{ pm.expect(jsonData['{k}']).to.eql({val_repr}); }});")
                else:
                    val_repr = json.dumps(v)
                    exec_script.append(f"pm.test(\"Check {k}\", function () {{ pm.expect(jsonData['{k}']).to.eql({val_repr}); }});")
                    
        else:
            # Plain String
            safe_str = str(expected_response).replace('"', '\\"')
            
            # Smart Assertion: Only assert strict text match if it doesn't look like a variable placeholder
            # If it contains "<" and ">", assume it's a template and skip strict content check
            if "<" in safe_str and ">" in safe_str:
                 exec_script.append(f"// Skipped strict body match because expected response contains placeholders: {safe_str}")
            else:
                 exec_script.append(f"pm.test(\"Body contains expected text\", function () {{")
                 exec_script.append(f"    pm.expect(pm.response.text()).to.include(\"{safe_str}\");")
                 exec_script.append("});")

    event = [
        {
            "listen": "test",
            "script": {
                "exec": exec_script,
                "type": "text/javascript"
            }
        }
    ]

    return {
        "name": name,
        "request": pm_request,
        "event": event
    }
