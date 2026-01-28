import urllib.request
import urllib.parse
import os
import mimetypes

url = "http://localhost:8000/api/upload"
file_path = "sample_api.xlsx"
result_file = "verify_result.txt"

def log(msg):
    # Print to stdout (even if not captured)
    print(msg)
    # Write to file
    try:
        with open(result_file, "a") as f:
            f.write(msg + "\n")
    except Exception as e:
        pass # Can't log logging failure

# Clean up previous result
if os.path.exists(result_file):
    try:
        os.remove(result_file)
    except:
        pass

if not os.path.exists(file_path):
    log(f"Error: {file_path} not found in {os.getcwd()}")
    exit(1)

log(f"Uploading {file_path} to {url}...")

# Create multipart body manually since we don't have requests
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = []
body.append(f'--{boundary}')
body.append(f'Content-Disposition: form-data; name="file"; filename="{file_path}"')
body.append('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
body.append('')
with open(file_path, 'rb') as f:
    body.append(f.read())
body.append(f'--{boundary}--')
body.append('')

# Combine body parts
final_body = b''
for part in body:
    if isinstance(part, str):
        final_body += part.encode('utf-8') + b'\r\n'
    else:
        final_body += part + b'\r\n'

req = urllib.request.Request(url, data=final_body)
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

try:
    with urllib.request.urlopen(req) as response:
        status = response.getcode()
        content = response.read().decode('utf-8')
        log(f"Status Code: {status}")
        log(f"Response: {content}")
        if status == 200:
            log("SUCCESS: Upload verified.")
        else:
            log("FAILURE: Upload status not 200.")
except urllib.error.HTTPError as e:
    log(f"FAILURE: HTTP Error {e.code}")
    log(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    log(f"EXCEPTION: {e}")
