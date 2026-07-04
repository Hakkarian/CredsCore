"""Synthetic Data Service - Minimal FastAPI Application.

Generates privacy-safe synthetic credit application data using CTGAN.
"""

import sys
import os
import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Optional

import logging
import uuid

import httpx
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from app.gan_engine import (
        get_or_create_engine,
        CTGANEngine,
        create_sample_training_data,
    )
except ImportError:
    # torch/ctgan not available — use simple engine only
    get_or_create_engine = None
    CTGANEngine = None
    create_sample_training_data = None

from app.simple_engine import get_simple_engine
from app.models import (
    GenerationRequest,
    GenerationResponse,
    GenerationWithAnalysisRequest,
    SyntheticRecord,
    CreditFeatures,
    QualityMetrics,
)
from app.config import config

# Credit Scoring service URL for downstream drift + peer-group analysis
CREDIT_SCORING_URL = os.getenv("CREDIT_SCORING_URL", "http://localhost:8001")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Global engine reference
current_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global current_engine
    logger.info("Synthetic Data Service starting up...")

    # Initialize model in background thread to avoid blocking startup
    if get_or_create_engine is not None:
        import threading
        def init_model():
            global current_engine
            try:
                current_engine = get_or_create_engine()
                logger.info("Model initialized successfully")
            except Exception as e:
                logger.warning(f"Model initialization failed: {e}")

        threading.Thread(target=init_model, daemon=True).start()
    else:
        logger.info("CTGAN unavailable — using simple statistical engine")

    yield

    logger.info("Synthetic Data Service shutting down...")


app = FastAPI(
    title="Synthetic Data Service",
    description="Privacy-safe synthetic credit data generation using CTGAN",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def calculate_quality_metrics(df: pd.DataFrame) -> QualityMetrics:
    """Calculate basic quality metrics."""
    total_records = len(df)
    valid_records = 0

    for _, row in df.iterrows():
        is_valid = True
        for feature_name, ranges in config.feature_ranges.items():
            if feature_name in df.columns:
                value = row[feature_name]
                if not (ranges["min"] <= value <= ranges["max"]):
                    is_valid = False
                    break
        if is_valid:
            valid_records += 1

    validity_score = valid_records / total_records if total_records > 0 else 0.0

    # Compute similarity score from feature distribution statistics
    # Compare generated data distributions against expected real-world distributions
    feature_stats = {
        'RevolvingUtilizationOfUnsecuredLines': {'mean': 0.35, 'std': 0.25},
        'DebtRatio': {'mean': 0.40, 'std': 0.28},
        'MonthlyIncome': {'mean': 6500, 'std': 4000},
        'age': {'mean': 42, 'std': 13},
        'NumberOfOpenCreditLinesAndLoans': {'mean': 8, 'std': 5},
    }

    stat_deviations = []
    for feat, expected in feature_stats.items():
        if feat in df.columns:
            gen_mean = df[feat].mean()
            gen_std = df[feat].std() if len(df) > 1 else expected['std']
            mean_diff = abs(gen_mean - expected['mean']) / (expected['std'] + 1e-8)
            std_diff = abs(gen_std - expected['std']) / (expected['std'] + 1e-8)
            stat_deviations.append((mean_diff + std_diff) / 2)

    avg_deviation = sum(stat_deviations) / len(stat_deviations) if stat_deviations else 1.0
    similarity_score = max(0.3, min(0.98, 1.0 - avg_deviation * 0.5))

    # Compute privacy score based on uniqueness of records
    # More unique records = better privacy (less likely to memorize real data)
    if len(df) > 1:
        try:
            duplicated_ratio = df.duplicated().sum() / len(df)
            privacy_score = max(0.5, min(0.99, 0.95 - duplicated_ratio * 0.5))
        except Exception:
            privacy_score = 0.85
    else:
        privacy_score = 0.85

    overall_score = similarity_score * 0.4 + privacy_score * 0.4 + validity_score * 0.2

    return QualityMetrics(
        similarity_score=round(similarity_score, 3),
        privacy_score=round(privacy_score, 3),
        validity_score=round(validity_score, 3),
        overall_score=round(overall_score, 3),
    )


def dataframe_to_records(df: pd.DataFrame, generation_id: str) -> list:
    """Convert DataFrame to list of SyntheticRecord."""
    records = []
    for idx, row in df.iterrows():
        features = CreditFeatures(
            RevolvingUtilizationOfUnsecuredLines=float(
                row.get("RevolvingUtilizationOfUnsecuredLines", 0.5)
            ),
            age=int(row.get("age", 30)),
            NumberOfTime30_59DaysPastDueNotWorse=int(
                row.get("NumberOfTime30_59DaysPastDueNotWorse", 0)
            ),
            DebtRatio=float(row.get("DebtRatio", 0.3)),
            MonthlyIncome=float(row.get("MonthlyIncome", 5000.0)),
            NumberOfOpenCreditLinesAndLoans=int(
                row.get("NumberOfOpenCreditLinesAndLoans", 5)
            ),
            NumberOfTimes90DaysLate=int(row.get("NumberOfTimes90DaysLate", 0)),
            NumberRealEstateLoansOrLines=int(
                row.get("NumberRealEstateLoansOrLines", 0)
            ),
            NumberOfTime60_89DaysPastDueNotWorse=int(
                row.get("NumberOfTime60_89DaysPastDueNotWorse", 0)
            ),
            NumberOfDependents=int(row.get("NumberOfDependents", 0)),
        )
        record = SyntheticRecord(
            record_id=f"{generation_id}_{idx}",
            features=features,
            generated_at=datetime.now(timezone.utc),
        )
        records.append(record)
    return records


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "service": "synthetic-data",
        "model_ready": current_engine is not None and getattr(current_engine, 'is_trained', False),
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Synthetic Data Service",
        "version": "1.0.0",
        "description": "Privacy-safe synthetic credit data generation using CTGAN",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "health": "GET /health",
            "generate": "POST /generate",
            "generate-with-analysis": "POST /generate-with-analysis",
        },
    }


@app.post("/generate", response_model=GenerationResponse)
async def generate_data(request: GenerationRequest):
    """Generate synthetic credit application data.

    Uses simplified statistical sampling for instant results.
    """
    try:
        from app.simple_engine import get_simple_engine

        logger.info(f"Generating {request.num_records} synthetic records...")

        # Use simple engine for instant generation
        engine = get_simple_engine()
        df = engine.generate(
            num_records=request.num_records,
            random_seed=request.random_seed,
        )

        # Convert to records
        generation_id = str(uuid.uuid4())
        records = dataframe_to_records(df, generation_id)

        # Calculate metrics
        quality_metrics = calculate_quality_metrics(df)

        return GenerationResponse(
            num_records=len(records),
            records=records,
            quality_metrics=quality_metrics,
            generated_at=datetime.now(timezone.utc),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


async def _post_analysis(client: httpx.AsyncClient, url: str, params: dict, batch: list) -> tuple:
    """POST a batch to an analysis endpoint. Returns (result_dict, None) or (None, error_str)."""
    try:
        resp = await client.post(url, params=params, json=batch)
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)}"


@app.post("/generate-with-analysis")
async def generate_with_analysis(request: GenerationWithAnalysisRequest):
    """Generate synthetic data and auto-compute drift + peer-group analysis.

    Generation failures raise HTTPException; downstream analysis failures are
    best-effort and surfaced via the ``*_error`` fields in the response.
    """
    try:
        logger.info(f"Generating {request.num_records} synthetic records for combined analysis...")

        # Reuse the same generation pipeline as /generate
        engine = get_simple_engine()
        df = engine.generate(
            num_records=request.num_records,
            random_seed=request.random_seed,
        )
        generation_id = str(uuid.uuid4())
        records = dataframe_to_records(df, generation_id)
        quality_metrics = calculate_quality_metrics(df)

        # Batch payload: list of feature dicts with underscore field names
        batch = [r.features.model_dump() for r in records]

        async with httpx.AsyncClient(timeout=60.0) as client:
            tasks = []
            if request.include_drift:
                tasks.append(
                    _post_analysis(
                        client,
                        f"{CREDIT_SCORING_URL}/monitor-drift",
                        {"n_clusters": request.drift_n_clusters},
                        batch,
                    )
                )
            if request.include_peer_groups:
                tasks.append(
                    _post_analysis(
                        client,
                        f"{CREDIT_SCORING_URL}/peer-groups",
                        {"n_clusters": request.peer_n_clusters},
                        batch,
                    )
                )

            results = await asyncio.gather(*tasks, return_exceptions=True)

        drift_result, drift_error = None, None
        peer_groups_result, peer_groups_error = None, None
        idx = 0
        if request.include_drift:
            res = results[idx]
            idx += 1
            if isinstance(res, Exception):
                drift_error = f"{type(res).__name__}: {str(res)}"
            else:
                drift_result, drift_error = res
        if request.include_peer_groups:
            res = results[idx]
            if isinstance(res, Exception):
                peer_groups_error = f"{type(res).__name__}: {str(res)}"
            else:
                peer_groups_result, peer_groups_error = res

        return {
            "num_records": len(records),
            "records": [r.model_dump() for r in records],
            "quality_metrics": quality_metrics.model_dump(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "drift": drift_result,
            "peer_groups": peer_groups_result,
            "drift_error": drift_error,
            "peer_groups_error": peer_groups_error,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate-with-analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.port,
        reload=config.debug,
    )
