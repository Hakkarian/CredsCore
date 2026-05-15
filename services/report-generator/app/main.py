import sys
sys.path.insert(0, "/app/shared")

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import os
import uuid
from datetime import datetime

from credscore_shared import HealthCheckResponse
from pydantic import BaseModel, Field
from typing import Optional


class ReportRequest(BaseModel):
    applicant_name: str
    score: float
    risk_level: str
    decision: str


class ReportResponse(BaseModel):
    report_id: str
    status: str


class ReportStatusResponse(BaseModel):
    report_id: str
    status: str
    content: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

app = FastAPI(title="Report Generator Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

reports: Dict[str, Dict[str, Any]] = {}


def generate_report(report_id: str, req: ReportRequest):
    reports[report_id]["status"] = "generating"
    reports[report_id]["content"] = f"""CREDIT REPORT
================
Applicant: {req.applicant_name}
Date: {datetime.utcnow().isoformat()}
Score: {req.score}
Risk Level: {req.risk_level}
Decision: {req.decision}
================
This is a generated credit report."""
    reports[report_id]["status"] = "completed"
    reports[report_id]["completed_at"] = datetime.utcnow().isoformat()


@app.get("/health", response_model=HealthCheckResponse)
def health():
    return HealthCheckResponse(status="healthy", details={"service_name": "report-generator"})


@app.post("/generate")
def generate(req: ReportRequest, background_tasks: BackgroundTasks):
    report_id = str(uuid.uuid4())
    reports[report_id] = {
        "id": report_id,
        "applicant_name": req.applicant_name,
        "score": req.score,
        "risk_level": req.risk_level,
        "decision": req.decision,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }
    background_tasks.add_task(generate_report, report_id, req)
    return ReportResponse(report_id=report_id, status="pending")


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="Report not found")
    r = reports[report_id]
    return ReportStatusResponse(
        report_id=r["id"],
        status=r["status"],
        content=r.get("content"),
        created_at=r["created_at"],
        completed_at=r.get("completed_at"),
    )


@app.get("/")
def root():
    return {"service": "report-generator", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)