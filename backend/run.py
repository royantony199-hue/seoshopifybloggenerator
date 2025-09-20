import os
import subprocess
import sys

def main():
    port = os.environ.get("PORT", "8000")
    print(f"Starting on port: {port}")
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", port
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    main()