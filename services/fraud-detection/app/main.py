import sys
sys.path.insert(0, "/app/shared")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import numpy as np

from credscore_shared import (
    ClientData,
    ApplicantScoreResponse,
    FraudRingStatsResponse,
    ScanStatusResponse,
    HealthCheckResponse,
)
from app.faiss_service import FAISSService

app = FastAPI(title="Fraud Detection Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

faiss_service: Optional[FAISSService] = None


@app.on_event("startup")
async def startup():
    global faiss_service
    model_dir = os.getenv("MODEL_DIR", "/app/saved_models")
    try:
        faiss_service = FAISSService(model_dir)
    except Exception as e:
        print(f"FAISS not loaded: {e}")


@app.get("/health", response_model=HealthCheckResponse)
def health():
    return HealthCheckResponse(
        status="healthy" if faiss_service else "unhealthy",
        service_name="fraud-detection",
        dependencies={"faiss": str(faiss_service is not None)},
    )


@app.post("/similar")
def find_similar(cd: ClientData, k: int = 10):
    if not faiss_service:
        raise HTTPException(status_code=503, detail="FAISS not loaded")
    try:
        features = np.array([
            cd.RevolvingUtilizationOfUnsecuredLines,
            cd.age,
            cd.NumberOfTime30_59DaysPastDueNotWorse,
            cd.DebtRatio,
            cd.MonthlyIncome,
            cd.NumberOfOpenCreditLinesAndLoans,
            cd.NumberOfTimes90DaysLate,
            cd.NumberRealEstateLoansOrLines,
            cd.NumberOfTime60_89DaysPastDueNotWorse,
            cd.NumberOfDependents or 0,
        ], dtype=np.float32)
        return faiss_service.find_similar(features, k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fraud-rings")
def get_fraud_rings():
    return {"total_rings": 0, "rings": [], "status": "ok"}


@app.get("/fraud-rings/status")
def get_scan_status():
    return {"last_scan_time": None, "is_scanning": False, "fraud_rings_detected": 0}


@app.get("/")
def root():
    return {"service": "fraud-detection", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)