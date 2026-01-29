import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"
TARGET_URL = "http://localhost:3000"  # Juice Shop or similar

def test_flow():
    print(f"[+] Starting scan on {TARGET_URL}...")
    
    # 1. Start Attack
    try:
        resp = requests.post(f"{BASE_URL}/attack", json={"url": TARGET_URL})
        resp.raise_for_status()
        data = resp.json()
        run_id = data["runId"]
        print(f"[+] Scan started. Run ID: {run_id}")
    except Exception as e:
        print(f"[-] Failed to start scan: {e}")
        sys.exit(1)

    # 2. Poll Status
    print("[+] Polling status...")
    while True:
        try:
            status_resp = requests.get(f"{BASE_URL}/status/{run_id}")
            status_resp.raise_for_status()
            status_data = status_resp.json()
            
            status = status_data["status"]
            print(f"    Status: {status}")
            
            if status in ["COMPLETE", "ERROR"]:
                if status == "ERROR":
                    print("[-] Scan failed with ERROR status.")
                    print(json.dumps(status_data, indent=2))
                    sys.exit(1)
                
                # 3. Verify Report
                report = status_data.get("report")
                if not report:
                    print("[-] Status is COMPLETE but 'report' is missing/null!")
                    sys.exit(1)
                
                print("[+] Scan COMPLETE. Verifying report structure...")
                required_keys = ["summary", "vulnerabilities", "risk_level"]
                missing = [k for k in required_keys if k not in report]
                
                if missing:
                    print(f"[-] Report is missing keys: {missing}")
                    print(json.dumps(report, indent=2))
                    sys.exit(1)
                
                if not isinstance(report["summary"], str):
                     print(f"[-] Report 'summary' is not a string! Type: {type(report['summary'])}")
                     sys.exit(1)

                print("[SUCCESS] Report received and valid!")
                print(f"    Risk Level: {report['risk_level']}")
                print(f"    Vulnerabilities: {len(report['vulnerabilities'])}")
                print(f"    Summary: {report['summary'][:100]}...")
                break
            
            time.sleep(2)
            
        except Exception as e:
            print(f"[-] Polling failed: {e}")
            break

if __name__ == "__main__":
    test_flow()
