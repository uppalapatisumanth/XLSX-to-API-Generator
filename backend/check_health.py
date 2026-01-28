import urllib.request
import json
import time

print("Checking Backend Health...")
url = "http://127.0.0.1:8000/health"

for i in range(5):
    try:
        with urllib.request.urlopen(url) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                print(f"SUCCESS: {data}")
                exit(0)
    except Exception as e:
        print(f"Attempt {i+1}: Failed ({e})")
        time.sleep(1)

print("FAILURE: Backend not reachable.")
exit(1)
