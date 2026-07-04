"""Pydantic models for the Synthetic Data Service."""

from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CreditFeatures(BaseModel):
    """Credit application features schema."""

    RevolvingUtilizationOfUnsecuredLines: float = Field(..., ge=0.0, le=1.0)
    age: int = Field(..., ge=18, le=100)
    NumberOfTime30_59DaysPastDueNotWorse: int = Field(..., ge=0, le=10)
    DebtRatio: float = Field(..., ge=0.0, le=2.0)
    MonthlyIncome: float = Field(..., ge=1000.0, le=50000.0)
    NumberOfOpenCreditLinesAndLoans: int = Field(..., ge=0, le=30)
    NumberOfTimes90DaysLate: int = Field(..., ge=0, le=10)
    NumberRealEstateLoansOrLines: int = Field(..., ge=0, le=10)
    NumberOfTime60_89DaysPastDueNotWorse: int = Field(..., ge=0, le=10)
    NumberOfDependents: int = Field(..., ge=0, le=10)


class SyntheticRecord(BaseModel):
    """A single synthetic credit application record."""

    record_id: str = Field(..., description="Unique record identifier")
    features: CreditFeatures = Field(..., description="Credit features")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QualityMetrics(BaseModel):
    """Quality metrics for synthetic data."""

    similarity_score: float = Field(..., ge=0.0, le=1.0)
    privacy_score: float = Field(..., ge=0.0, le=1.0)
    validity_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)


class GenerationRequest(BaseModel):
    """Request to generate synthetic data."""

    num_records: int = Field(..., ge=1, le=10000, description="Number of records")
    apply_constraints: bool = Field(default=True, description="Apply constraints")
    random_seed: Optional[int] = Field(None, description="Random seed")


class GenerationWithAnalysisRequest(GenerationRequest):
    """Request to generate synthetic data and auto-compute drift + peer-group analysis."""

    drift_n_clusters: int = Field(10, ge=2, le=20, description="Clusters for drift monitoring")
    peer_n_clusters: int = Field(5, ge=2, le=20, description="Segments for peer-group analysis")
    include_drift: bool = Field(True, description="Compute drift analysis")
    include_peer_groups: bool = Field(True, description="Compute peer-group analysis")


class GenerationResponse(BaseModel):
    """Response from synthetic data generation."""

    num_records: int = Field(..., description="Number of records generated")
    records: List[SyntheticRecord] = Field(..., description="Generated records")
    quality_metrics: QualityMetrics = Field(..., description="Quality metrics")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
