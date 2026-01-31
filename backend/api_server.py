import os
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from core.orchestrator import Orchestrator

# Load environment variables
load_dotenv()

app = FastAPI(title="Security Scanner API")

# Manual CORS Middleware to bypass strict checks
class ManualCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("Origin", "*")
        
        # Log for debugging
        print(f"DEBUG: {request.method} {request.url} | Origin: {origin}")

        # Handle Preflight OPTIONS directly
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

        try:
            response = await call_next(request)
        except Exception as e:
            print(f"ERROR: {e}")
            response = JSONResponse(content={"detail": str(e)}, status_code=500)

        # Set CORS headers on all responses
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

app.add_middleware(ManualCORSMiddleware)

# In-memory storage for scan state
scans: Dict[str, dict] = {}
scan_locks = {}


class ScanRequest(BaseModel):
    url: str


class ScanResponse(BaseModel):
    runId: str


class StatusResponse(BaseModel):
    status: str
    logs: List[dict]
    report: Optional[dict] = None


def add_log(run_id: str, message: str, log_type: str = "info"):
    """Thread-safe log addition"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "message": message,
        "type": log_type
    }
    
    if run_id in scans:
        scans[run_id]["logs"].append(log_entry)


def run_scan(run_id: str, target_url: str):
    """Run the security scan in a background thread"""
    try:
        add_log(run_id, f"Starting security scan on {target_url}", "info")
        scans[run_id]["status"] = "SCANNING"
        
        # Create orchestrator with custom target
        add_log(run_id, "[Step 1] Initializing ZAP client", "step")
        orchestrator = Orchestrator(
            target_url=target_url,
            log_callback=lambda msg, log_type="info": add_log(run_id, msg, log_type)
        )
        
        add_log(run_id, "[Step 2] Running security orchestrator", "step")
        result = orchestrator.run()
        
        findings = result.get("findings", [])
        attack_surface = result.get("attack_surface", [])
        
        # Generate Frontend-compatible report
        summary_text = f"Scan completed on {target_url}. Found {len(findings)} vulnerabilities."
        if not findings:
            summary_text += " No significant security issues were detected."
        else:
            summary_text += " Immediate remediation is recommended."

        scans[run_id]["report"] = {
            "target": target_url,
            "timestamp": datetime.now().isoformat(),
            "risk_level": result.get("risk_level", "LOW"),
            "summary": summary_text, # MUST BE STRING
            "vulnerabilities": [
                {
                    "type": f.get("vulnerability"),
                    "severity": f.get("severity"),
                    "location": f.get("endpoint"),
                    "description": f"Impact: {f.get('impact')}. Parameter: {f.get('parameter')}"
                }
                for f in findings
            ],
            "pages_visited": [item.get("url") for item in attack_surface if item.get("url")],
            "inputs_tested": [], # We can populate this if we track it
            "recommendations": [
                "Implement strict input validation",
                "Enable Content Security Policy (CSP)",
                "Review access controls on all endpoints"
            ] if findings else ["Regularly update dependencies", "Enable CSP"]
        }
        
        add_log(run_id, "Scan complete. Report ready.", "success")
        
        # Update scan with results - AFTER report is ready to avoid race condition with frontend polling
        scans[run_id]["findings"] = findings
        scans[run_id]["status"] = "COMPLETE"
            
    except Exception as e:
        scans[run_id]["status"] = "ERROR"
        add_log(run_id, f"Scan failed: {str(e)}", "error")
        print(f"[ERROR] Scan {run_id} failed: {e}")


@app.post("/attack", response_model=ScanResponse)
async def start_attack(request: ScanRequest):
    """Start a new security scan"""
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Generate unique run ID
    run_id = str(uuid.uuid4())
    
    # Initialize scan state
    scans[run_id] = {
        "status": "INITIALIZING",
        "logs": [],
        "findings": [],
        "report": None,
        "target_url": request.url,
        "created_at": datetime.now().isoformat()
    }
    
    # Start scan in background thread
    thread = threading.Thread(target=run_scan, args=(run_id, request.url), daemon=True)
    thread.start()
    
    return ScanResponse(runId=run_id)


@app.get("/status/{run_id}", response_model=StatusResponse)
async def get_status(run_id: str):
    """Get the current status of a scan"""
    if run_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan = scans[run_id]
    
    return StatusResponse(
        status=scan["status"],
        logs=scan["logs"],
        report=scan.get("report")
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_scans": len([s for s in scans.values() if s["status"] == "SCANNING"])
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
