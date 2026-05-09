import sys
import os
import asyncio
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import numpy as np
import pandas as pd

from credscore_shared import (
    FraudDetectionClientData,
    ApplicantScoreResponse,
    FraudRingResponse,
    ScanStatusResponse,
    HealthCheckResponse,
)
from app.faiss_service import FAISSService
from app.snn_fraud_detector import SNNFraudDetector
from app.batch_processor import BatchFraudProcessor

# Global state
faiss_service: Optional[FAISSService] = None
batch_processor: Optional[BatchFraudProcessor] = None


def _resolve_data_path() -> str:
    """Resolve the training data path, checking multiple locations."""
    # Check environment variable first
    env_path = os.getenv("TRAINING_DATA_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # Check relative to this file
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "data", "cs-training.csv"),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "cs-training.csv"),
        "data/cs-training.csv",
    ]
    for path in candidates:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            return abs_path

    return os.path.join(os.path.dirname(__file__), "..", "data", "cs-training.csv")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle handler."""
    global faiss_service, batch_processor

    model_dir = os.getenv(
        "MODEL_DIR", os.path.join(os.path.dirname(__file__), "..", "saved_models")
    )
    data_path = _resolve_data_path()

    # Initialize FAISS service
    try:
        faiss_service = FAISSService(model_dir)
        print(f"FAISS service loaded from {model_dir}")
    except Exception as e:
        print(f"FAISS not loaded: {e}")

    # Initialize batch processor (SNN fraud ring detection)
    try:
        batch_processor = BatchFraudProcessor(
            data_path=data_path,
            save_dir=model_dir,
        )
        batch_processor.initialize()
        print(f"Batch processor initialized (data: {data_path})")
    except Exception as e:
        print(f"Batch processor initialization failed: {e}")
        # Create a minimal processor without data
        batch_processor = BatchFraudProcessor(data_path=data_path, save_dir=model_dir)

    yield

    # Shutdown cleanup
    faiss_service = None
    batch_processor = None


app = FastAPI(title="Fraud Detection Service", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/health", response_model=HealthCheckResponse)
def health():
    snn_loaded = batch_processor is not None and batch_processor.snn_detector is not None
    snn_rings = len(batch_processor.snn_detector.fraud_rings) if snn_loaded else 0
    return HealthCheckResponse(
        status="healthy" if faiss_service else "degraded",
        timestamp=datetime.utcnow(),
        details={
            "service_name": "fraud-detection",
            "dependencies": {
                "faiss": faiss_service is not None and faiss_service.loaded,
                "snn_detector": snn_loaded,
                "faiss_is_dummy": faiss_service is not None and not faiss_service.loaded,
            },
            "fraud_rings_detected": snn_rings,
        },
    )


@app.post("/similar")
@app.get("/similar")
def find_similar(k: int = 10, cd: Optional[FraudDetectionClientData] = None):
    if not faiss_service:
        raise HTTPException(status_code=503, detail="FAISS not loaded")
    try:
        if cd is None:
            # For GET requests without body, return empty result
            return {"similar_applicants": [], "total": 0, "message": "POST with client data required for similarity search"}
        features = np.array(
            [
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
            ],
            dtype=np.float32,
        )
        return faiss_service.find_similar(features, k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fraud-rings")
def get_fraud_rings():
    """Get all detected fraud rings."""
    if not batch_processor or not batch_processor.snn_detector:
        return {"total_rings": 0, "rings": [], "status": "snn_not_initialized"}

    stats = batch_processor.get_fraud_rings_cache()
    if not stats:
        return {"total_rings": 0, "rings": [], "status": "no_scan_run"}

    return {
        "total_rings": stats.get("total_rings_detected", 0),
        "rings": stats.get("rings", []),
        "high_risk": stats.get("high_risk_rings", 0),
        "medium_risk": stats.get("medium_risk_rings", 0),
        "low_risk": stats.get("low_risk_rings", 0),
        "status": "ok",
    }


@app.post("/fraud-rings/scan")
async def trigger_fraud_scan():
    """Trigger a fraud ring detection scan."""
    if not batch_processor:
        raise HTTPException(status_code=503, detail="Batch processor not initialized")

    if batch_processor.scan_in_progress:
        return {"status": "scan_already_in_progress", "message": "A scan is currently running"}

    try:
        result = await batch_processor.run_scan()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fraud-rings/status", response_model=ScanStatusResponse)
def get_scan_status():
    if not batch_processor:
        return ScanStatusResponse(
            last_scan_time=None,
            is_scanning=False,
            scan_interval_minutes=60,
            fraud_rings_detected=0,
            faiss_index_size=0,
        )
    status = batch_processor.get_scan_status()
    return ScanStatusResponse(
        last_scan_time=status.get("last_scan_time"),
        is_scanning=status.get("is_scanning", False),
        scan_interval_minutes=status.get("scan_interval_minutes", 60),
        fraud_rings_detected=status.get("fraud_rings_detected", 0),
        faiss_index_size=status.get("faiss_index_size", 0),
    )


@app.get("/fraud-rings/{ring_id}")
def get_fraud_ring(ring_id: str):
    """Get details for a specific fraud ring."""
    if not batch_processor:
        raise HTTPException(status_code=504, detail="Batch processor not initialized")
    ring = batch_processor.get_fraud_ring_by_id(ring_id)
    if not ring:
        raise HTTPException(status_code=404, detail=f"Fraud ring {ring_id} not found")
    return ring


@app.get("/")
def root():
    return {
        "service": "fraud-detection",
        "version": "2.0.0",
        "faiss_loaded": faiss_service is not None and faiss_service.loaded,
        "snn_initialized": batch_processor is not None and batch_processor.snn_detector is not None,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
