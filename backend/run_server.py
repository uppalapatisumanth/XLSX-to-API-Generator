import sys
import traceback
import os

log_file = "server_log.txt"

def log(msg):
    with open(log_file, "a") as f:
        f.write(msg + "\n")

if os.path.exists(log_file):
    os.remove(log_file)

try:
    log("Initializing...")
    import uvicorn
    log("Uvicorn imported.")
    
    # Check imports
    try:
        from services import parser
        log("Parser imported.")
    except Exception as e:
        log(f"Parser import failed: {e}")
        raise

    try:
        from services import postman_generator
        log("Postman Generator imported.")
    except Exception as e:
        log(f"Postman Generator import failed: {e}")
        raise

    import main
    log("Main module imported.")

    log("Starting Uvicorn Server on port 8000...")
    # Run programmatically
    uvicorn.run(main.app, host="127.0.0.1", port=8000)

except Exception:
    log("CRITICAL FAILURE:")
    log(traceback.format_exc())
