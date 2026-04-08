import sys
sys.path.insert(0, "/app/shared")

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import httpx
import os
import uuid
from datetime import datetime

from credscore_shared import (
    HealthCheckResponse,
    ClientData,
    LoanApplicationRequest,
    LoanApplicationResponse,
    ApplicationStatus,
)

app = FastAPI(title="Orchestrator Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CREDIT_SCORING_URL = os.getenv("CREDIT_SCORING_URL", "http://credit-scoring:8000")
FRAUD_DETECTION_URL = os.getenv("FRAUD_DETECTION_URL", "http://fraud-detection:8000")
POLICY_URL = os.getenv("POLICY_URL", "http://policy:8000")
ENRICHMENT_URL = os.getenv("ENRICHMENT_URL", "http://data-enrichment:8000")

applications: Dict[str, Dict[str, Any]] = {}


async def call_service(url: str, endpoint: str, payload: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{url}/{endpoint}", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()


async def process_application(app_id: str, applicant: ClientData):
    try:
        applications[app_id]["status"] = "processing"
        applications[app_id]["steps"]["enrichment"] = "running"
        enrichment = await call_service(ENRICHMENT_URL, "enrich", applicant.model_dump())
        applications[app_id]["steps"]["enrichment"] = "complete"
        applications[app_id]["enrichment"] = enrichment

        applications[app_id]["steps"]["credit_scoring"] = "running"
        score = await call_service(CREDIT_SCORING_URL, "score", {"applicant": applicant.model_dump(), "use_rgcn": True})
        applications[app_id]["steps"]["credit_scoring"] = "complete"
        applications[app_id]["score"] = score

        applications[app_id]["steps"]["fraud_check"] = "running"
        fraud = await call_service(FRAUD_DETECTION_URL, "similar", applicant.model_dump())
        applications[app_id]["steps"]["fraud_check"] = "complete"
        applications[app_id]["fraud"] = fraud

        fraud_score = fraud.get("avg_distance", 0)
        probability = score.get("base_probability", 0)

        applications[app_id]["steps"]["policy"] = "running"
        policy = await call_service(POLICY_URL, "evaluate", {"probability": probability, "fraud_score": fraud_score})
        applications[app_id]["steps"]["policy"] = "complete"
        applications[app_id]["policy"] = policy

        applications[app_id]["status"] = policy["decision"]
        applications[app_id]["completed_at"] = datetime.utcnow().isoformat()
    except Exception as e:
        applications[app_id]["status"] = "error"
        applications[app_id]["error"] = str(e)


@app.get("/health", response_model=HealthCheckResponse)
def health():
    return HealthCheckResponse(status="healthy", service_name="orchestrator", dependencies={})


@app.post("/apply")
async def apply(req: LoanApplicationRequest, background_tasks: BackgroundTasks):
    app_id = str(uuid.uuid4())
    applications[app_id] = {
        "id": app_id,
        "applicant": req.applicant.model_dump(),
        "status": "pending",
        "steps": {"enrichment": "pending", "credit_scoring": "pending", "fraud_check": "pending", "policy": "pending"},
        "created_at": datetime.utcnow().isoformat(),
    }
    background_tasks.add_task(process_application, app_id, req.applicant)
    return {"application_id": app_id, "status": "pending"}


@app.get("/applications/{app_id}")
def get_application(app_id: str):
    if app_id not in applications:
        raise HTTPException(status_code=404, detail="Application not found")
    return applications[app_id]


@app.get("/")
def root():
    return {"service": "orchestrator", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)