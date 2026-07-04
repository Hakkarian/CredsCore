import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import httpx

from credscore_shared import HealthCheckResponse, ClientData, EnrichmentResponse

app = FastAPI(title="Data Enrichment Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


async def fetch_credit_bureau(applicant: ClientData) -> Dict[str, Any]:
    return {
        "bureau_score": 720,
        "tradelines": 5,
        "inquiries_6m": 2,
        "public_records": 0,
    }


async def fetch_open_banking(applicant: ClientData) -> Dict[str, Any]:
    return {
        "avg_balance": 15000,
        "transaction_count_3m": 150,
        "overdraft_count": 0,
        "income_estimate": 5000,
    }


@app.get("/health", response_model=HealthCheckResponse)
def health():
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        details={
            "service_name": "data-enrichment",
            "dependencies": {"credit_bureau": "mock", "open_banking": "mock"},
        },
    )


@app.post("/enrich")
async def enrich(applicant: ClientData):
    bureau = await fetch_credit_bureau(applicant)
    banking = await fetch_open_banking(applicant)
    return EnrichmentResponse(
        applicant_id=None,
        credit_bureau_data=bureau,
        open_banking_data=banking,
        status="complete",
    )


@app.get("/")
def root():
    return {"service": "data-enrichment", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
