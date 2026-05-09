import sys
import os

# Add shared library path for local development
shared_path = os.path.join(os.path.dirname(__file__), "..", "..", "shared")
sys.path.insert(0, shared_path)

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from credscore_shared import (
    HealthCheckResponse,
    PolicyDecisionRequest,
    PolicyDecisionResponse,
)
from app.policy import RiskPolicy, assess_risk

app = FastAPI(title="Policy Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
engine = RiskPolicy()


@app.get("/health", response_model=HealthCheckResponse)
def health():
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        details={"service_name": "policy", "dependencies": {"engine": "loaded"}},
    )


@app.post("/evaluate", response_model=PolicyDecisionResponse)
def evaluate(req: PolicyDecisionRequest):
    result = assess_risk(
        risk_score=req.risk_score,
        monthly_income=req.monthly_income,
        debt_ratio=req.debt_ratio,
        employment_months=req.employment_months,
        recent_inquiries=req.recent_inquiries,
        requested_amount=req.requested_amount,
    )
    return PolicyDecisionResponse(**result)


@app.get("/")
def root():
    return {"service": "policy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
