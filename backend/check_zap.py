import os
import sys
import time
import requests
from dotenv import load_dotenv

def check_zap():
    load_dotenv()
    
    zap_url = os.getenv("ZAP_PROXY_URL", "http://127.0.0.1:8080")
    api_key = os.getenv("ZAP_API_KEY", "changeme")
    
    print(f"[+] Checking ZAP connectivity at {zap_url}...")
    
    # Try connecting to the root or a safe API endpoint
    try:
        # Check simple connectivity
        resp = requests.get(zap_url, timeout=5)
        print(f"[+] ZAP is reachable! (Status: {resp.status_code})")
        
        # Check API access
        api_check_url = f"{zap_url}/JSON/core/view/version/?apikey={api_key}"
        resp = requests.get(api_check_url, timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"[+] API Valid. ZAP Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print("[-] ZAP reachable but API Key seems invalid or rejected.")
            print(f"    Response: {resp.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[-] Could not connect to ZAP. Is it running?")
        print("    Run 'start_zap_daemon.ps1' or start it manually.")
        return False
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = check_zap()
    if not success:
        sys.exit(1)
