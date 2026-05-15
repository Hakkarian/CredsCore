import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from credscore_shared import (
    HealthCheckResponse,
    ClientData,
    LoanApplicationRequest,
    ServiceClient,
)

CREDIT_SCORING_URL = os.getenv("CREDIT_SCORING_URL", "http://localhost:8001")
FRAUD_DETECTION_URL = os.getenv("FRAUD_DETECTION_URL", "http://localhost:8002")
POLICY_URL = os.getenv("POLICY_URL", "http://localhost:8003")
ENRICHMENT_URL = os.getenv("ENRICHMENT_URL", "http://localhost:8006")

# Service Clients
clients: Dict[str, ServiceClient] = {}

# In-memory application store
applications: Dict[str, Dict[str, Any]] = {}

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    clients["enrichment"] = ServiceClient(ENRICHMENT_URL)
    clients["scoring"] = ServiceClient(CREDIT_SCORING_URL)
    clients["fraud"] = ServiceClient(FRAUD_DETECTION_URL)
    clients["policy"] = ServiceClient(POLICY_URL)
    logger.info("Orchestrator started with service clients initialized")
    yield
    # Shutdown
    for client in clients.values():
        await client.close()
    clients.clear()


app = FastAPI(title="Orchestrator Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


def _extract_applicant_features(applicant: ClientData) -> Dict[str, Any]:
    """Extract ML-compatible features from ClientData for downstream services."""
    return {
        "RevolvingUtilizationOfUnsecuredLines": applicant.RevolvingUtilizationOfUnsecuredLines,
        "age": applicant.age,
        "NumberOfTime30_59DaysPastDueNotWorse": applicant.NumberOfTime30_59DaysPastDueNotWorse,
        "DebtRatio": applicant.DebtRatio,
        "MonthlyIncome": applicant.MonthlyIncome,
        "NumberOfOpenCreditLinesAndLoans": applicant.NumberOfOpenCreditLinesAndLoans,
        "NumberOfTimes90DaysLate": applicant.NumberOfTimes90DaysLate,
        "NumberRealEstateLoansOrLines": applicant.NumberRealEstateLoansOrLines,
        "NumberOfTime60_89DaysPastDueNotWorse": applicant.NumberOfTime60_89DaysPastDueNotWorse,
        "NumberOfDependents": applicant.NumberOfDependents or 0,
    }


async def process_application(
    app_id: str, applicant: ClientData, requested_amount: float
):
    try:
        applications[app_id]["status"] = "processing"

        # Step 1: Enrichment
        applications[app_id]["steps"]["enrichment"] = "running"
        enrichment = await clients["enrichment"].post(
            "enrich", json=applicant.model_dump()
        )
        applications[app_id]["steps"]["enrichment"] = "complete"
        applications[app_id]["enrichment"] = enrichment

        # Step 2: Credit scoring — send actual applicant data
        applications[app_id]["steps"]["credit_scoring"] = "running"
        score = await clients["scoring"].post(
            "score",
            json={"applicant": applicant.model_dump(), "use_rgcn": True},
        )
        applications[app_id]["steps"]["credit_scoring"] = "complete"
        applications[app_id]["score"] = score

        # Step 3: Fraud detection — send actual applicant features, not hardcoded
        applications[app_id]["steps"]["fraud_check"] = "running"
        fraud_payload = _extract_applicant_features(applicant)
        fraud = await clients["fraud"].post("similar", json=fraud_payload)
        applications[app_id]["steps"]["fraud_check"] = "complete"
        applications[app_id]["fraud"] = fraud

        # Extract probability from the actual /similar response shape:
        # { total, default_count, default_rate, estimated_probability,
        #   risk_assessment, avg_distance, ... }
        probability = score.get("base_probability", 0)

        # Step 4: Policy evaluation — send full payload, not just risk_score + amount
        applications[app_id]["steps"]["policy"] = "running"
        policy = await clients["policy"].post(
            "evaluate",
            json={
                "risk_score": probability,
                "requested_amount": requested_amount,
                "monthly_income": enrichment.get("open_banking_data", {}).get(
                    "monthly_income", 0
                ),
                "debt_ratio": enrichment.get("credit_bureau_data", {}).get(
                    "debt_ratio", 0
                ),
                "employment_months": enrichment.get("credit_bureau_data", {}).get(
                    "employment_months", 0
                ),
                "recent_inquiries": enrichment.get("credit_bureau_data", {}).get(
                    "recent_inquiries", 0
                ),
            },
        )
        applications[app_id]["steps"]["policy"] = "complete"
        applications[app_id]["policy"] = policy

        applications[app_id]["status"] = policy["decision"]
        applications[app_id]["completed_at"] = datetime.utcnow().isoformat()

    except Exception as e:
        applications[app_id]["status"] = "error"
        applications[app_id]["error"] = str(e)


@app.get("/health", response_model=HealthCheckResponse)
def health():
    return HealthCheckResponse(
        status="healthy", details={"service_name": "orchestrator"}
    )


class ApplicationResponse(BaseModel):
    """Typed response for application status."""

    id: str
    applicant: Dict[str, Any]
    status: str
    requested_amount: float = 0.0
    steps: Dict[str, str] = {}
    created_at: str = ""
    completed_at: Optional[str] = None
    score: Optional[Dict[str, Any]] = None
    fraud: Optional[Dict[str, Any]] = None
    policy: Optional[Dict[str, Any]] = None
    enrichment: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.post("/apply")
async def apply(req: LoanApplicationRequest, background_tasks: BackgroundTasks):
    app_id = str(uuid.uuid4())
    applications[app_id] = {
        "id": app_id,
        "applicant": req.applicant.model_dump(),
        "status": "pending",
        "requested_amount": req.requested_amount,
        "steps": {
            "enrichment": "pending",
            "credit_scoring": "pending",
            "fraud_check": "pending",
            "policy": "pending",
        },
        "created_at": datetime.utcnow().isoformat(),
    }
    background_tasks.add_task(
        process_application, app_id, req.applicant, req.requested_amount
    )
    return {"application_id": app_id, "status": "pending"}


@app.get("/applications/{app_id}", response_model=ApplicationResponse)
def get_application(app_id: str):
    if app_id not in applications:
        raise HTTPException(status_code=404, detail="Application not found")
    return applications[app_id]


@app.get("/")
def root():
    return {"service": "orchestrator", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
