"""Pydantic models for unified augmented scoring service."""
from datetime import datetime
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field


# ============ Core Scoring Models ============

class ApplicantFeatures(BaseModel):
    """Applicant data features."""
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


class BaseMLScore(BaseModel):
    """Base ML model prediction."""
    default_probability: float = Field(ge=0.0, le=1.0)
    prediction: int
    risk_level: Literal["low", "medium", "high"]
    confidence: float = Field(ge=0.0, le=1.0)


class AugmentedScoreRequest(BaseModel):
    """Request for augmented credit scoring."""
    applicant_id: str
    features: ApplicantFeatures
    entity_id: Optional[str] = None
    include_causal: bool = True
    include_social: bool = True
    treatment: Literal["approve", "deny", "higher_rate", "lower_rate"] = "approve"


# ============ Causal Inference Models ============

class PropensityResult(BaseModel):
    """Propensity score estimation."""
    score: float = Field(ge=0.0, le=1.0)
    tier: Literal["low", "medium", "high"]
    method: str = "logistic_regression"


class TreatmentEffectResult(BaseModel):
    """Treatment effect estimate."""
    method: str
    ate: float
    confidence_interval: tuple[float, float]
    p_value: float
    standard_error: float


class CounterfactualScenario(BaseModel):
    """Counterfactual outcome."""
    treatment: str
    predicted_outcome: float
    outcome_probability: float
    risk_change: float
    recommendation: str


class CausalInferenceResult(BaseModel):
    """Causal inference analysis."""
    propensity_score: PropensityResult
    treatment_effects: List[TreatmentEffectResult]
    counterfactuals: List[CounterfactualScenario]
    optimal_decision: str
    expected_improvement: float
    recommendation: str
    confidence: float


# ============ Social Capital Models ============

class SocialMetrics(BaseModel):
    """Social capital metrics."""
    centrality: float = Field(ge=0.0, le=1.0)
    influence: float = Field(ge=0.0, le=1.0)
    trust: float = Field(ge=0.0, le=1.0)
    reach: float = Field(ge=0.0, le=1.0)
    engagement: float = Field(ge=0.0, le=1.0)
    communities: int


class NetworkRiskIndicators(BaseModel):
    """Network-based risk indicators."""
    fraud_risk: float = Field(ge=0.0, le=1.0, default=0.3)
    default_risk: float = Field(ge=0.0, le=1.0, default=0.5)
    reputational_risk: float = Field(ge=0.0, le=1.0, default=0.4)


class SocialCapitalResult(BaseModel):
    """Social capital analysis."""
    scores: SocialMetrics
    network_size: int
    connection_count: int
    risk_indicators: NetworkRiskIndicators
    analysis_summary: str
    social_credit_score: int = Field(ge=300, le=850)


class NetworkVisualizationData(BaseModel):
    """Network data for visualization."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    communities: int


# ============ Combined Result Models ============

class FeatureWeight(BaseModel):
    """Contribution weight of each feature."""
    ml_weight: float
    causal_weight: float
    social_weight: float


class AugmentedScoreResult(BaseModel):
    """Complete augmented credit score result."""
    applicant_id: str
    timestamp: datetime

    # Base ML score
    base_ml: BaseMLScore

    # Causal inference (optional)
    causal_inference: Optional[CausalInferenceResult] = None

    # Social capital (optional)
    social_capital: Optional[SocialCapitalResult] = None

    # Combined score
    combined_risk_score: float = Field(ge=0.0, le=1.0)
    combined_risk_level: Literal["low", "medium", "high"]
    combined_decision: Literal["approve", "deny", "review"]
    recommended_rate: float

    # Feature contributions
    feature_weights: FeatureWeight

    # Human explanation
    explanation: str


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    services: Dict[str, bool]


class ScoreComponentsRequest(BaseModel):
    """Request to get individual score components."""
    applicant_id: str
    component: Literal["ml", "causal", "social", "all"]
