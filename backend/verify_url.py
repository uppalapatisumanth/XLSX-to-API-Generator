import sys
sys.path.append('d:/ais/api/backend')
from services.parser import parse_xlsx
import pandas as pd
import io

def test_url_parsing():
    print("Testing URL Parsing...")
    # Create mock Excel
    df = pd.DataFrame([{
        'API Name': 'Test',
        'HTTP Method': 'GET',
        'Endpoint URL': 'https://mock.com/api/v1/resource',
        'Ref ID': '1',
        'Module/Feature': 'General'
    }])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='apis', index=False)
        
    data = output.getvalue()
    result, errors = parse_xlsx(data)
    
    print(f"Errors: {errors}")
    base_url = result.get("env", {}).get("base_url")
    print(f"Base URL: {base_url}")
    
    path = result["apis"][0]["url"]
    print(f"Path: {path}")
    
    if base_url == "https://mock.com" and path == "/api/v1/resource":
        print("SUCCESS: URL split correctly.")
        exit(0)
    else:
        print("FAILURE: URL split incorrect.")
        exit(1)

if __name__ == "__main__":
    test_url_parsing()
