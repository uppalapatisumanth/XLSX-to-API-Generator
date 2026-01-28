import pandas as pd
import requests
import json
import time

# Create a sample Excel with new columns
data = [
    {
        "Ref ID": "REF-001",
        "Module/Feature": "Auth",
        "API Name": "Login",
        "HTTP Method": "POST",
        "Endpoint URL": "/api/login",
        "Headers Required": "Content-Type: application/json",
        "Request Payload (JSON example)": '{"user": "admin", "pass": "123"}',
        "Expected Response (Success)": '{"token": "xyz"}'
    },
    {
        "Ref ID": "REF-002",
        "Module/Feature": "Users",
        "API Name": "Get Profile",
        "HTTP Method": "GET",
        "Endpoint URL": "/api/profile",
        "Headers Required": "Authorization: Bearer <token>",
        "Request Payload (JSON example)": "",
        "Expected Response (Success)": '{"id": 1}'
    }
]

file_name = "test_strict.xlsx"
df = pd.DataFrame(data)
df.to_excel(file_name, index=False)
print(f"Created {file_name}")

# Upload
url = "http://localhost:8000/api/upload"
with open(file_name, "rb") as f:
    files = {"file": f}
    print("Uploading...")
    res = requests.post(url, files=files)
    
if res.status_code != 200:
    print(f"Upload Failed: {res.text}")
    exit(1)

task_id = res.json()["task_id"]
print(f"Task ID: {task_id}")

# Poll Status
print("Polling status...")
for i in range(10):
    time.sleep(1)
    res = requests.get(f"http://localhost:8000/api/status/{task_id}")
    status = res.json()
    print(f"Status: {status['status']}")
    
    if status['status'] == 'completed':
        print("\n--- API Preview Data ---")
        preview = status.get('api_preview', [])
        print(json.dumps(preview, indent=2))
        
        # Verify fields
        if len(preview) == 2 and preview[0]['module'] == 'Auth':
            print("\nSUCCESS: Strict parsing and preview verified.")
        else:
            print("\nFAILURE: Data mistmatch.")
        break
    elif status['status'] == 'failed':
        print(f"Processing Failed: {status['logs']}")
        break
