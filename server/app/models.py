from pydantic import BaseModel, Field
from typing import List, Optional


class ClientData(BaseModel):
    # Features from the training data
    RevolvingUtilizationOfUnsecuredLines: float = Field(..., ge=0, description="Revolving utilization of unsecured lines")
    age: int = Field(..., ge=18, le=100, description="Age of the client")
    NumberOfTime30_59DaysPastDueNotWorse: int = Field(..., ge=0, description="Number of times 30-59 days past due")
    DebtRatio: float = Field(..., ge=0, description="Debt ratio")
    MonthlyIncome: float = Field(..., ge=0, description="Monthly income")
    NumberOfOpenCreditLinesAndLoans: int = Field(..., ge=0, description="Number of open credit lines and loans")
    NumberOfTimes90DaysLate: int = Field(..., ge=0, description="Number of times 90 days late")
    NumberRealEstateLoansOrLines: int = Field(..., ge=0, description="Number of real estate loans or lines")
    NumberOfTime60_89DaysPastDueNotWorse: int = Field(..., ge=0, description="Number of times 60-89 days past due")
    NumberOfDependents: Optional[int] = Field(0, ge=0, description="Number of dependents")


# ============================================================
# Enhanced models for full risk assessment (article-based design)
# ============================================================

class CreditReportSignals(BaseModel):
    """Behavioral credit signals from credit report."""
    payment_consistency_score: Optional[float] = Field(None, ge=0, le=1, description="Payment consistency over time (0-1)")
    credit_history_months: Optional[int] = Field(None, ge=0, description="Length of credit history in months")
    recent_inquiries: Optional[int] = Field(0, ge=0, description="Number of recent credit inquiries")
    prior_defaults: Optional[int] = Field(0, ge=0, description="Number of prior defaults or delinquencies")
    revolving_utilization: Optional[float] = Field(None, ge=0, le=1, description="Current revolving credit utilization")


class FinancialStabilitySignals(BaseModel):
    """Financial stability signals."""
    monthly_income: Optional[float] = Field(None, ge=0, description="Monthly income in local currency")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual income in local currency")
    debt_to_income_ratio: Optional[float] = Field(None, ge=0, description="Debt-to-income ratio")
    monthly_repayment_pressure: Optional[float] = Field(None, ge=0, description="Monthly repayment burden")
    employment_tenure_months: Optional[int] = Field(None, ge=0, description="Months in current employment")


class StructuralProfile(BaseModel):
    """Structural profile signals."""
    employment_status: Optional[str] = Field(None, description="Employment status (employed, self-employed, unemployed)")
    loan_purpose: Optional[str] = Field(None, description="Purpose of the loan")
    education_level: Optional[str] = Field(None, description="Education level")
    loan_amount_requested: Optional[float] = Field(None, ge=0, description="Requested loan amount in local currency")


class CreditApplicationRequest(BaseModel):
    """Full credit application request with all signal types."""
    # Core ML features (required for ML model)
    RevolvingUtilizationOfUnsecuredLines: float = Field(..., ge=0, description="Revolving utilization of unsecured lines")
    age: int = Field(..., ge=18, le=100, description="Age of the client")
    NumberOfTime30_59DaysPastDueNotWorse: int = Field(..., ge=0, description="Number of times 30-59 days past due")
    DebtRatio: float = Field(..., ge=0, description="Debt ratio")
    MonthlyIncome: float = Field(..., ge=0, description="Monthly income")
    NumberOfOpenCreditLinesAndLoans: int = Field(..., ge=0, description="Number of open credit lines and loans")
    NumberOfTimes90DaysLate: int = Field(..., ge=0, description="Number of times 90 days late")
    NumberRealEstateLoansOrLines: int = Field(..., ge=0, description="Number of real estate loans or lines")
    NumberOfTime60_89DaysPastDueNotWorse: int = Field(..., ge=0, description="Number of times 60-89 days past due")
    NumberOfDependents: Optional[int] = Field(0, ge=0, description="Number of dependents")
    
    # Enhanced signals (optional, used by policy engine)
    credit_report: Optional[CreditReportSignals] = Field(None, description="Behavioral credit signals")
    financial_stability: Optional[FinancialStabilitySignals] = Field(None, description="Financial stability signals")
    structural_profile: Optional[StructuralProfile] = Field(None, description="Structural profile signals")

    def get_monthly_income(self) -> float:
        """Get monthly income from best available source."""
        if self.financial_stability and self.financial_stability.monthly_income:
            return self.financial_stability.monthly_income
        return self.MonthlyIncome

    def get_recent_inquiries(self) -> int:
        """Get recent inquiries from credit report."""
        if self.credit_report and self.credit_report.recent_inquiries:
            return self.credit_report.recent_inquiries
        return 0

    def get_employment_tenure(self) -> int:
        """Get employment tenure from financial stability signals."""
        if self.financial_stability and self.financial_stability.employment_tenure_months:
            return self.financial_stability.employment_tenure_months
        return 0

    def get_requested_amount(self) -> Optional[float]:
        """Get requested loan amount."""
        if self.structural_profile and self.structural_profile.loan_amount_requested:
            return self.structural_profile.loan_amount_requested
        return None


class PolicyAssessment(BaseModel):
    """Policy engine assessment result."""
    decision: str = Field(..., description="Policy decision: APPROVE, REVIEW, or DECLINE")
    risk_grade: str = Field(..., description="Risk grade: A (excellent) to E (very high risk)")
    interest_rate: float = Field(..., description="Risk-adjusted interest rate percentage")
    recommended_max_amount: Optional[float] = Field(None, description="Maximum recommended loan amount")
    rationale: str = Field(..., description="Decision rationale for explainability")
    conditions: List[str] = Field(default_factory=list, description="Conditions or flags raised")
    policy_version: str = Field("v1.0", description="Policy version for audit trail")


class RiskAssessmentResponse(BaseModel):
    """Full risk assessment response combining ML and policy."""
    # ML Risk Estimation (Layer 1)
    risk_score: float = Field(..., description="ML risk score (0-1)")
    default_probability: float = Field(..., description="Default probability from model")
    top_risk_factors: List[dict] = Field(default_factory=list, description="Top SHAP-based risk factors")

    # Policy Decision (Layer 2)
    policy: PolicyAssessment = Field(..., description="Policy engine assessment")

    # Human-readable summary
    human_summary: str = Field(..., description="Plain language explanation for sales/risk teams")
    tier_message: str = Field(..., description="Quick summary for customer communication")


# ============================================================
# FAISS + SNN Fraud Detection models
# ============================================================

class FraudRingMemberInfo(BaseModel):
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
    members: List[FraudRingMemberInfo]


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
    fraud_indicator: dict
    risk_level: str
    neighbor_stats: dict
    fraud_rings: List[dict] = []


class ScanStatusResponse(BaseModel):
    last_scan_time: Optional[str]
    is_scanning: bool
    scan_interval_minutes: int
    fraud_rings_detected: int
    faiss_index_size: int
