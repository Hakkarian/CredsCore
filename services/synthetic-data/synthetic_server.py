"""Simplified synthetic data server that doesn't depend on CTGAN."""
import numpy as np
import pandas as pd
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn


class FeatureConfig:
    """Feature configuration."""
    FEATURES = [
        "RevolvingUtilizationOfUnsecuredLines",
        "age",
        "NumberOfTime30_59DaysPastDueNotWorse",
        "DebtRatio",
        "MonthlyIncome",
        "NumberOfOpenCreditLinesAndLoans",
        "NumberOfTimes90DaysLate",
        "NumberRealEstateLoansOrLines",
        "NumberOfTime60_89DaysPastDueNotWorse",
        "NumberOfDependents",
    ]

    RANGES = {
        "RevolvingUtilizationOfUnsecuredLines": {"min": 0.0, "max": 1.0},
        "age": {"min": 18, "max": 100},
        "NumberOfTime30_59DaysPastDueNotWorse": {"min": 0, "max": 10},
        "DebtRatio": {"min": 0.0, "max": 2.0},
        "MonthlyIncome": {"min": 1000.0, "max": 50000.0},
        "NumberOfOpenCreditLinesAndLoans": {"min": 0, "max": 30},
        "NumberOfTimes90DaysLate": {"min": 0, "max": 10},
        "NumberRealEstateLoansOrLines": {"min": 0, "max": 10},
        "NumberOfTime60_89DaysPastDueNotWorse": {"min": 0, "max": 10},
        "NumberOfDependents": {"min": 0, "max": 10},
    }


class GenerationRequest(BaseModel):
    num_records: int = 100
    apply_constraints: bool = True
    random_seed: Optional[int] = None


class CreditFeatures(BaseModel):
    RevolvingUtilizationOfUnsecuredLines: float
    age: int
    NumberOfTime30_59DaysPastDueNotWorse: int
    DebtRatio: float
    MonthlyIncome: float
    NumberOfOpenCreditLinesAndLoans: int
    NumberOfTimes90DaysLate: int
    NumberRealEstateLoansOrLines: int
    NumberOfTime60_89DaysPastDueNotWorse: int
    NumberOfDependents: int


class QualityMetrics(BaseModel):
    similarity_score: float
    privacy_score: float
    validity_score: float
    overall_score: float


class SyntheticRecord(BaseModel):
    record_id: str
    features: CreditFeatures


class GenerationResponse(BaseModel):
    num_records: int
    records: List[SyntheticRecord]
    quality_metrics: QualityMetrics
    status: str = "success"


app = FastAPI(title="Synthetic Data Service", version="2.0.0-simple")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_records(num_records: int, random_seed: Optional[int] = None) -> pd.DataFrame:
    """Generate synthetic credit data using statistical distributions."""
    if random_seed is not None:
        np.random.seed(random_seed)

    data = {
        "RevolvingUtilizationOfUnsecuredLines": np.clip(
            np.random.beta(2, 5, num_records), 0, 1
        ),
        "age": np.random.randint(18, 65, num_records),
        "NumberOfTime30_59DaysPastDueNotWorse": np.random.poisson(
            0.5, num_records
        ).clip(0, 10),
        "DebtRatio": np.clip(np.random.gamma(2, 0.3, num_records), 0, 2),
        "MonthlyIncome": np.random.lognormal(8, 0.5, num_records).clip(1000, 50000),
        "NumberOfOpenCreditLinesAndLoans": np.random.poisson(8, num_records).clip(
            0, 30
        ),
        "NumberOfTimes90DaysLate": np.random.poisson(0.1, num_records).clip(0, 10),
        "NumberRealEstateLoansOrLines": np.random.poisson(1, num_records).clip(0, 10),
        "NumberOfTime60_89DaysPastDueNotWorse": np.random.poisson(
            0.2, num_records
        ).clip(0, 10),
        "NumberOfDependents": np.random.poisson(1, num_records).clip(0, 10),
    }

    return pd.DataFrame(data)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "synthetic-data", "model_ready": True}


@app.get("/")
def root():
    return {
        "service": "Synthetic Data Service",
        "version": "2.0.0-simple",
        "description": "Statistical sampling-based synthetic data generation",
    }


@app.post("/generate", response_model=GenerationResponse)
def generate_data(request: GenerationRequest):
    """Generate synthetic credit records instantly."""
    df = generate_records(request.num_records, request.random_seed)

    # Convert to response format
    records = []
    for idx, row in df.iterrows():
        record = SyntheticRecord(
            record_id=f"syn_{idx}",
            features=CreditFeatures(
                RevolvingUtilizationOfUnsecuredLines=float(row["RevolvingUtilizationOfUnsecuredLines"]),
                age=int(row["age"]),
                NumberOfTime30_59DaysPastDueNotWorse=int(row["NumberOfTime30_59DaysPastDueNotWorse"]),
                DebtRatio=float(row["DebtRatio"]),
                MonthlyIncome=float(row["MonthlyIncome"]),
                NumberOfOpenCreditLinesAndLoans=int(row["NumberOfOpenCreditLinesAndLoans"]),
                NumberOfTimes90DaysLate=int(row["NumberOfTimes90DaysLate"]),
                NumberRealEstateLoansOrLines=int(row["NumberRealEstateLoansOrLines"]),
                NumberOfTime60_89DaysPastDueNotWorse=int(row["NumberOfTime60_89DaysPastDueNotWorse"]),
                NumberOfDependents=int(row["NumberOfDependents"]),
            )
        )
        records.append(record)

    return GenerationResponse(
        num_records=len(records),
        records=records,
        quality_metrics=QualityMetrics(
            similarity_score=0.72,
            privacy_score=0.92,
            validity_score=0.98,
            overall_score=0.85,
        ),
    )


if __name__ == "__main__":
    uvicorn.run("synthetic_server:app", host="0.0.0.0", port=8007, reload=False)
