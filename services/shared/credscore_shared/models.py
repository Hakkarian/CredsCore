from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class RiskGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class Decision(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    DECLINE = "DECLINE"


class ClientData(BaseModel):
    RevolvingUtilizationOfUnsecuredLines: float = Field(..., ge=0)
    age: int = Field(..., ge=18, le=100)
    NumberOfTime30_59DaysPastDueNotWorse: int = Field(..., ge=0)
    DebtRatio: float = Field(..., ge=0)
    MonthlyIncome: float = Field(..., ge=0)
    NumberOfOpenCreditLinesAndLoans: int = Field(..., ge=0)
    NumberOfTimes90DaysLate: int = Field(..., ge=0)
    NumberRealEstateLoansOrLines: int = Field(..., ge=0)
    NumberOfTime60_89DaysPastDueNotWorse: int = Field(..., ge=0)
    NumberOfDependents: Optional[int] = Field(0, ge=0)


class CreditReportSignals(BaseModel):
    payment_consistency_score: Optional[float] = Field(None, ge=0, le=1)
    credit_history_months: Optional[int] = Field(None, ge=0)
    recent_inquiries: Optional[int] = Field(0, ge=0)
    prior_defaults: Optional[int] = Field(0, ge=0)
    revolving_utilization: Optional[float] = Field(None, ge=0, le=1)


class FinancialStabilitySignals(BaseModel):
    monthly_income: Optional[float] = Field(None, ge=0)
    annual_income: Optional[float] = Field(None, ge=0)
    debt_to_income_ratio: Optional[float] = Field(None, ge=0)
    monthly_repayment_pressure: Optional[float] = Field(None, ge=0)
    employment_tenure_months: Optional[int] = Field(None, ge=0)


class StructuralProfile(BaseModel):
    employment_status: Optional[str] = None
    loan_purpose: Optional[str] = None
    education_level: Optional[str] = None
    loan_amount_requested: Optional[float] = Field(None, ge=0)


class CreditApplicationRequest(BaseModel):
    RevolvingUtilizationOfUnsecuredLines: float = Field(..., ge=0)
    age: int = Field(..., ge=18, le=100)
    NumberOfTime30_59DaysPastDueNotWorse: int = Field(..., ge=0)
    DebtRatio: float = Field(..., ge=0)
    MonthlyIncome: float = Field(..., ge=0)
    NumberOfOpenCreditLinesAndLoans: int = Field(..., ge=0)
    NumberOfTimes90DaysLate: int = Field(..., ge=0)
    NumberRealEstateLoansOrLines: int = Field(..., ge=0)
    NumberOfTime60_89DaysPastDueNotWorse: int = Field(..., ge=0)
    NumberOfDependents: Optional[int] = Field(0, ge=0)

    credit_report: Optional[CreditReportSignals] = None
    financial_stability: Optional[FinancialStabilitySignals] = None
    structural_profile: Optional[StructuralProfile] = None

    def get_monthly_income(self) -> float:
        if self.financial_stability and self.financial_stability.monthly_income:
            return self.financial_stability.monthly_income
        return self.MonthlyIncome

    def get_recent_inquiries(self) -> int:
        if self.credit_report and self.credit_report.recent_inquiries:
            return self.credit_report.recent_inquiries
        return 0

    def get_employment_tenure(self) -> int:
        if self.financial_stability and self.financial_stability.employment_tenure_months:
            return self.financial_stability.employment_tenure_months
        return 0

    def get_requested_amount(self) -> Optional[float]:
        if self.structural_profile and self.structural_profile.loan_amount_requested:
            return self.structural_profile.loan_amount_requested
        return None


class RiskFactor(BaseModel):
    feature: str
    shap_value: float
    impact: str


class PolicyAssessment(BaseModel):
    decision: str
    risk_grade: str
    interest_rate: float
    recommended_max_amount: Optional[float] = None
    rationale: str
    conditions: List[str] = Field(default_factory=list)
    policy_version: str = "v1.0"


class RiskAssessmentResponse(BaseModel):
    risk_score: float
    default_probability: float
    top_risk_factors: List[RiskFactor] = Field(default_factory=list)
    policy: PolicyAssessment
    human_summary: str
    tier_message: str


class FraudRingMember(BaseModel):
    index: int
    risk_score: float
    anomaly_score: float
    shared_neighbors: int


class FraudRingResponse(BaseModel):
    ring_id: str
    member_count: int
    avg_risk_score: float
    avg_anomaly_score: float
    cohesiveness: float
    risk_level: str
    risk_factors: List[str]
    members: List[FraudRingMember]


class FraudRingStatsResponse(BaseModel):
    total_applicants: int
    total_rings_detected: int
    high_risk_rings: int
    medium_risk_rings: int
    low_risk_rings: int
    largest_ring_size: int
    avg_ring_size: float
    scan_timestamp: Optional[str] = None
    scan_duration_seconds: Optional[float] = None
    status: str = "ok"
    rings: List[FraudRingResponse] = []


class ApplicantScoreResponse(BaseModel):
    enhanced_risk_score: float
    base_neighbor_risk: float
    weighted_neighbor_risk: float
    default_neighbor_ratio: float
    anomaly_score: float
    fraud_indicator: Dict[str, Any]
    risk_level: str
    neighbor_stats: Dict[str, Any]
    fraud_rings: List[Dict[str, Any]] = []


class ScanStatusResponse(BaseModel):
    last_scan_time: Optional[str]
    is_scanning: bool
    scan_interval_minutes: int
    fraud_rings_detected: int
    faiss_index_size: int


class RGCNFeaturesResponse(BaseModel):
    embeddings: List[float]
    similarity_mean: float
    similarity_max: float
    similarity_min: float
    similarity_std: float
    feature_count: int


class ScoreRequest(BaseModel):
    applicant: ClientData
    use_rgcn: bool = False


class ScoreResult(BaseModel):
    base_probability: float
    rgcn_probability: Optional[float] = None
    risk_level: str
    top_risk_factors: List[RiskFactor]
    rgcn_features: Optional[RGCNFeaturesResponse] = None


class SimilarApplicantsRequest(BaseModel):
    applicant: ClientData
    k: int = 10


class SimilarApplicantsResult(BaseModel):
    similar_applicants: Dict[str, Any]
    interpretation: Dict[str, Any]
    human_explanation: str


class ThinFileRequest(BaseModel):
    applicant: ClientData
    k: int = 5


class ThinFileResult(BaseModel):
    base_prediction: Dict[str, Any]
    neighbor_features: Dict[str, Any]
    enhanced_prediction: Dict[str, Any]
    interpretation: Dict[str, Any]
    human_explanation: str


class ExplainDenialRequest(BaseModel):
    applicant: ClientData
    k: int = 20


class ExplainDenialResult(BaseModel):
    prediction: str
    default_probability: float
    denial_reasons: List[Dict[str, Any]]
    similar_approved_applicants: Dict[str, Any]
    human_explanation: str


class DriftRequest(BaseModel):
    data: List[Dict[str, Any]]
    n_clusters: int = 10


class DriftResult(BaseModel):
    drift_analysis: Dict[str, Any]
    interpretation: Dict[str, Any]
    human_explanation: str


class PeerGroupsRequest(BaseModel):
    data: List[Dict[str, Any]]
    n_clusters: int = 5


class PeerGroupsResult(BaseModel):
    total_customers: int
    n_segments: int
    segments: List[Dict[str, Any]]
    summary: Dict[str, Any]
    human_explanation: str


class ReportRequest(BaseModel):
    applicant: ClientData
    assessment: RiskAssessmentResponse
    report_type: str = "full"


class ReportStatusResponse(BaseModel):
    job_id: str
    status: str
    report_url: Optional[str] = None
    created_at: Optional[str] = None


class LoanApplicationRequest(BaseModel):
    applicant: CreditApplicationRequest
    requested_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    correlation_id: Optional[str] = None


class LoanApplicationResponse(BaseModel):
    application_id: str
    status: str
    correlation_id: Optional[str] = None
    risk_score: Optional[float] = None
    decision: Optional[str] = None
    report_job_id: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str
    service_name: str
    version: str = "1.0.0"
    dependencies: Dict[str, str] = Field(default_factory=dict)


class PolicyDecisionRequest(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    fraud_score: Optional[float] = Field(None, ge=0, le=1)


class PolicyDecisionResponse(BaseModel):
    decision: str
    risk_grade: str
    interest_rate: float
    recommended_max_amount: Optional[float] = None
    rationale: str
    conditions: List[str] = Field(default_factory=list)
    policy_version: str = "v1.0"
