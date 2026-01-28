
import logging
import sys
from pathlib import Path
import pandas as pd
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_default_template(path: Path):
    print(f"Attempting to generate template at: {path}")
    
    # Exact ordered columns
    columns = [
        "Ref ID", "Module/Feature", "API Name", "HTTP Method", "Endpoint URL",
        "Headers Required", "Request Payload (JSON example)", "URL Params",
        "Expected Response (Success)", "Token Variable", "Is Token Generator", "Auth Scope"
    ]
    
    # Sheet 1: APIs
    apis_data = [
        {
            "Ref ID": "AUTH-01",
            "Module/Feature": "Authentication",
            "API Name": "Get Auth Token",
            "HTTP Method": "POST",
            "Endpoint URL": "getAuthToken", 
            "Headers Required": "Content-Type: application/x-www-form-urlencoded",
            "Request Payload (JSON example)": json.dumps({
                "login.username": "demo_user",
                "login.password": "secret123",
                "tenantId": "demo-tenant"
            }),
            "URL Params": "",
            "Expected Response (Success)": '{"token": "<authToken>"}',
            "Token Variable": "authToken",
            "Is Token Generator": "TRUE",
            "Auth Scope": ""
        }
    ]
    
    # Sheet 2: Environments
    env_data = [
        {"Variable": "base_url", "Value": "https://api.example.com/v2"},
        {"Variable": "tenantId", "Value": "demo-tenant"}
    ]
    
    try:
        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            df_apis = pd.DataFrame(apis_data)
            df_apis = df_apis.reindex(columns=columns)
            df_apis.to_excel(writer, sheet_name='apis', index=False)
            pd.DataFrame(env_data).to_excel(writer, sheet_name='environments', index=False)
        print("SUCCESS: File created.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        import xlsxwriter
        print(f"xlsxwriter version: {xlsxwriter.__version__}")
    except ImportError:
        print("ERROR: xlsxwriter module is NOT installed/accessible.")

    base_path = Path("artifacts_storage")
    base_path.mkdir(exist_ok=True)
    template_path = base_path / "AI_API_Test_Template.xlsx"
    generate_default_template(template_path)
