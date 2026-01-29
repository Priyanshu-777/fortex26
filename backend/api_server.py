import os
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from core.orchestrator import Orchestrator

# Load environment variables
load_dotenv()

app = FastAPI(title="Security Scanner API")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        findings = orchestrator.run()
        
        # Update scan with results
        scans[run_id]["status"] = "COMPLETE"
        scans[run_id]["findings"] = findings
        
        # Generate report structure
        if findings:
            add_log(run_id, f"Scan complete. Found {len(findings)} vulnerabilities", "success")
            scans[run_id]["report"] = {
                "target": target_url,
                "timestamp": datetime.now().isoformat(),
                "findings": findings,
                "summary": {
                    "total": len(findings),
                    "critical": sum(1 for f in findings if f.get("severity") == "CRITICAL"),
                    "high": sum(1 for f in findings if f.get("severity") == "HIGH"),
                    "medium": sum(1 for f in findings if f.get("severity") == "MEDIUM"),
                    "low": sum(1 for f in findings if f.get("severity") == "LOW"),
                }
            }
        else:
            add_log(run_id, "Scan complete. No vulnerabilities found", "success")
            scans[run_id]["report"] = {
                "target": target_url,
                "timestamp": datetime.now().isoformat(),
                "findings": [],
                "summary": {
                    "total": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                }
            }
            
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
