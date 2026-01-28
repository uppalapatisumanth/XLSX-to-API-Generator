import pandas as pd
import io
import json

def parse_xlsx(file_content: bytes) -> tuple[dict, list[str]]:
    """
    Parses the API Documentation XLSX.
    Expects columns: Ref ID, Module/Feature, API Name, HTTP Method, Endpoint URL, Headers Required, Request Payload, Expected Response
    """
    print("[PARSER] Starting parse_xlsx...")
    print(f"[PARSER] Received {len(file_content)} bytes")
    
    warnings = []
    output = {
        "apis": [],
        "env": {},
        "rules": {}
    }

    try:
        print("[PARSER] Creating ExcelFile object...")
        xls = pd.ExcelFile(io.BytesIO(file_content))
        print(f"[PARSER] ExcelFile created. Sheets: {xls.sheet_names}")
    except Exception as e:
        print(f"[PARSER] ERROR creating ExcelFile: {e}")
        return None, [f"Failed to read Excel file: {str(e)}"]

    # --- 1. Validate Sheet Existence ---
    target_sheet = None
    if "apis" in xls.sheet_names:
        target_sheet = "apis"
    else:
        # Fallback
        target_sheet = xls.sheet_names[0]
    
    print(f"[PARSER] Using sheet: {target_sheet}")
    df = pd.read_excel(xls, sheet_name=target_sheet)
    print(f"[PARSER] Sheet loaded. Shape: {df.shape}")

    # --- 1b. Parse Environments Sheet (Optional) ---
    if "environments" in xls.sheet_names:
        print("[PARSER] Found 'environments' sheet, parsing variables...")
        env_df = pd.read_excel(xls, sheet_name="environments")
        # Expecting columns like "Variable" and "Value" (or similar)
        # We will try to just grab everything that looks like a key-value pair
        # Let's normalize headers
        env_df.columns = [str(c).strip().lower() for c in env_df.columns]
        
        # Look for 'variable'/'key' and 'value'/'current value'
        key_col = next((c for c in env_df.columns if c in ['variable', 'key', 'name']), None)
        val_col = next((c for c in env_df.columns if c in ['value', 'initial value', 'current value']), None)
        
        if key_col and val_col:
            for _, row in env_df.iterrows():
                k = str(row[key_col]).strip()
                v = row[val_col]
                if pd.notna(k) and k:
                    output["env"][k] = str(v) if pd.notna(v) else ""
        else:
             print("[PARSER] 'environments' sheet found but could not identify Key/Value columns. Skipping.")

    
    # helper to normalize col name for matching
    def norm(c): return str(c).strip().lower().replace('\n', ' ')

    # Mapping: Normalized -> Internal Key
    col_map = {
        "ref id": "ref_id",
        "module/feature": "module",
        "api name": "name",
        "http method": "method",
        "endpoint url": "url",
        "headers required": "headers",
        "request payload (json example)": "body",
        "url params": "url_params",
        "expected response (success)": "expected_response",
        "auth scope": "auth_scope",
        "token variable": "token_variable",
        "is token generator": "is_token_generator"
    }

    # Identify actual columns
    actual_cols = {norm(c): c for c in df.columns}
    
    # Check strict requirements
    missing = []
    found_map = {} # Internal Key -> Actual Column Name
    
    for req_key, internal_key in col_map.items():
        # Fuzzy match
        match = None
        if req_key in actual_cols:
            match = actual_cols[req_key]
        else:
            for ac_norm, ac_orig in actual_cols.items():
                if req_key in ac_norm or ac_norm in req_key: 
                    match = ac_orig
                    break
        
        if match:
            found_map[internal_key] = match
        else:
            if internal_key in ["name", "method", "url"]:
                missing.append(req_key)

    if missing:
        return None, [f"Missing required columns in sheet '{target_sheet}': {', '.join(missing)}"]

    # Iterate rows
    for index, row in df.iterrows():
        row_num = index + 2
        item = {}
        
        def get_val(k):
             if k not in found_map: return None
             val = row[found_map[k]]
             if pd.isna(val) or str(val).strip() == "": return None
             return val

        # Basic Fields
        item["name"] = str(get_val("name") or "Untitled").strip()
        item["method"] = str(get_val("method") or "GET").strip().upper()
        raw_url = str(get_val("url") or "/").strip()
        
        # Smart URL Logic: Check for absolute URL
        if raw_url.lower().startswith("http"):
            # Split into base and path
            # Try to split after domain. Simple strategy: 3rd slash
            parts = raw_url.split("/", 3)
            if len(parts) >= 3:
                # Reconstruct base: protocol//domain
                base = f"{parts[0]}//{parts[2]}"
                # Path is the rest
                path_val = f"/{parts[3]}" if len(parts) > 3 else "/"
                
                item["url"] = path_val
                # Store detected base url in env global if not already set or override?
                # For now, let's just make sure we capture it. We'll prioritize the first one found.
                if "base_url" not in output["env"]:
                    output["env"]["base_url"] = base
            else:
                 # Fallback for weird urls
                 item["url"] = raw_url
        else:
            item["url"] = raw_url
        item["ref_id"] = str(get_val("ref_id") or "").strip()
        item["module"] = str(get_val("module") or "General").strip()
        
        # Body
        raw_body = get_val("body")
        item["body"] = {}
        item["body_mode"] = "json" # Default for new parsing
        if raw_body:
            try:
                item["body"] = _parse_strict_json(raw_body)
            except:
                warnings.append(f"Row {row_num}: Invalid JSON in body.")
        
        # Headers
        raw_headers = get_val("headers")
        item["headers"] = _parse_headers(raw_headers)
        
        # Auto-detect body_mode from headers
        # If Content-Type implies urlencoded, override default 'json'
        ct = item["headers"].get("Content-Type", "").lower()
        if "x-www-form-urlencoded" in ct:
            item["body_mode"] = "urlencoded"

        # Expected Response
        raw_resp = get_val("expected_response")
        item["expected_response"] = _safe_parse(raw_resp)
        
        item["status"] = 200
        
        # Authentication Fields
        item["auth_scope"] = str(get_val("auth_scope") or "").strip()
        
        # Token Validation: If users paste the entire token into 'Token Variable', detect and fix.
        raw_token_var = str(get_val("token_variable") or "").strip()
        if len(raw_token_var) > 50 or "." in raw_token_var:
             # Likely a JWT or misconfiguration
             item["token_variable"] = "token"
        else:
             item["token_variable"] = raw_token_var or "token" # Default to 'token' if empty

        val_gen = get_val("is_token_generator")
        item["is_token_generator"] = str(val_gen).lower() in ['true', 'yes', '1'] if val_gen else False
        
        # URL Params (for form-urlencoded or query params)
        raw_url_params = get_val("url_params")
        item["params"] = {} # Use standard key expected by generator
        if raw_url_params:
            try:
                item["params"] = _parse_strict_json(raw_url_params)
                # If body is empty but params exist, use params as body for form-urlencoded
                # BUT only if it's meant to be a body. For GET, it should stay as params.
                
                # Logic: If method is not GET and content-type is urlencoded, assume body.
                content_type = item["headers"].get("Content-Type", "").lower()
                is_urlencoded = "form-urlencoded" in content_type
                
                if not item["body"] and is_urlencoded and item["method"] != "GET":
                     item["body"] = item["params"]
                     item["body_mode"] = "urlencoded"
            except:
                warnings.append(f"Row {row_num}: Invalid JSON in URL Params.")
        
        output["apis"].append(item)

    return output, warnings

def _parse_strict_json(value):
    if isinstance(value, (dict, list)): return value
    return json.loads(str(value))

def _safe_parse(value):
    try:
        return _parse_strict_json(value)
    except:
        return str(value)

def _parse_headers(value):
    if not value: return {}
    try:
        return json.loads(str(value))
    except:
        headers = {}
        for line in str(value).replace(';', '\n').split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                headers[k.strip()] = v.strip()
        return headers
