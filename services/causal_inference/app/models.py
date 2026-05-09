"""Pydantic models for causal inference service."""
from datetime import datetime
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field


class TreatmentData(BaseModel):
    """Treatment assignment data."""
    group: Literal["treatment", "control"]
    outcome: float
    features: Dict[str, float]


class PropensityRequest(BaseModel):
    """Request for propensity score estimation."""
    features: Dict[str, float]
    applicant_id: str


class PropensityResponse(BaseModel):
    """Response for propensity score estimation."""
    applicant_id: str
    propensity_score: float = Field(ge=0.0, le=1.0)
    treatment_probability: float = Field(ge=0.0, le=1.0)
    risk_tier: str
    method: str
    timestamp: datetime


class TreatmentEffectRequest(BaseModel):
    """Request for treatment effect estimation."""
    features: Dict[str, float]
    applicant_id: str
    treatment: Literal["approve", "deny", "higher_rate", "lower_rate"]
    method: Literal["matching", "ipw", "doubly_robust", "all"] = "all"


class TreatmentEffect(BaseModel):
    """Single treatment effect result."""
    method: str
    ate: float
    confidence_interval: tuple[float, float]
    p_value: float
    standard_error: float


class TreatmentEffectResponse(BaseModel):
    """Response for treatment effect estimation."""
    applicant_id: str
    treatment: str
    effects: List[TreatmentEffect]
    estimated_outcome_treated: float
    estimated_outcome_control: float
    sample_size: int
    timestamp: datetime


class CounterfactualScenario(BaseModel):
    """Single counterfactual scenario."""
    scenario_id: str
    treatment: str
    predicted_outcome: float
    outcome_probability: float
    risk_change: float
    recommendation: str


class CounterfactualRequest(BaseModel):
    """Request for counterfactual generation."""
    features: Dict[str, float]
    applicant_id: str
    scenarios: Optional[List[str]] = None


class CounterfactualResponse(BaseModel):
    """Response for counterfactual generation."""
    applicant_id: str
    actual_treatment: str
    scenarios: List[CounterfactualScenario]
    optimal_decision: str
    expected_improvement: float
    timestamp: datetime


class UpliftSegment(BaseModel):
    """Uplift modeling segment."""
    segment: str
    score: float
    percentile: float
    description: str
    recommended_action: str


class UpliftRequest(BaseModel):
    """Request for uplift modeling."""
    features: Dict[str, float]
    applicant_id: str


class UpliftResponse(BaseModel):
    """Response for uplift modeling."""
    applicant_id: str
    uplift_score: float = Field(ge=-1.0, le=1.0)
    segment: str
    treatment_responsiveness: str
    segments: List[UpliftSegment]
    recommendation: str
    timestamp: datetime


class CausalAnalysisSummary(BaseModel):
    """Complete causal analysis summary."""
    applicant_id: str
    propensity_score: float
    treatment_effects: List[TreatmentEffect]
    counterfactuals: List[CounterfactualScenario]
    uplift: UpliftSegment
    recommended_decision: str
    confidence: float
    timestamp: datetime
