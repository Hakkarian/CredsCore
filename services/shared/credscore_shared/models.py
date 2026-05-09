from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import numpy as np


class ClientData(BaseModel):
    client_id: str = Field(..., description="Unique identifier for the client")
    name: str = Field(..., description="Client's full name")
    email: str = Field(..., description="Client's email address")
    phone: str = Field(..., description="Client's phone number")
    address: str = Field(..., description="Client's physical address")
    credit_score: float = Field(
        ..., ge=0, le=1000, description="Credit score between 0 and 1000"
    )


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    DECLINED = "declined"
    REVIEW = "review"


class LoanApplicationRequest(BaseModel):
    applicant: ClientData
    requested_amount: float
    loan_purpose: str = "general"
    loan_term_months: int = 12


class LoanApplicationResponse(BaseModel):
    application_id: str
    status: str
    decision: str
    risk_score: Optional[float] = None
    risk_grade: Optional[str] = None
    interest_rate: Optional[float] = None
    recommended_amount: Optional[float] = None
    enrichment_result: Optional[Dict[str, Any]] = None
    fraud_check_result: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EnrichmentResponse(BaseModel):
    applicant_id: str
    credit_bureau_data: Dict[str, Any] = Field(default_factory=dict)
    open_banking_data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "complete"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FraudDetectionClientData(BaseModel):
    RevolvingUtilizationOfUnsecuredLines: float = Field(
        ..., description="Revolving utilization"
    )
    age: int = Field(..., description="Age of the client")
    NumberOfTime30_59DaysPastDueNotWorse: int = Field(
        0, description="Number of 30-59 days late payments"
    )
    DebtRatio: float = Field(..., description="Debt ratio")
    MonthlyIncome: float = Field(..., description="Monthly income")
    NumberOfOpenCreditLinesAndLoans: int = Field(
        0, description="Number of open credit lines"
    )
    NumberOfTimes90DaysLate: int = Field(
        0, description="Number of 90+ days late payments"
    )
    NumberRealEstateLoansOrLines: int = Field(
        0, description="Number of real estate loans"
    )
    NumberOfTime60_89DaysPastDueNotWorse: int = Field(
        0, description="Number of 60-89 days late payments"
    )
    NumberOfDependents: int = Field(0, description="Number of dependents")


class CreditApplicationRequest(BaseModel):
    applicant_id: str = Field(..., description="Unique identifier for the applicant")
    monthly_income: float = Field(..., ge=0, description="Monthly income in NGN")
    loan_amount: float = Field(..., ge=0, description="Requested loan amount in NGN")
    employment_months: int = Field(
        ..., ge=0, description="Months of employment stability"
    )
    recent_inquiries: int = Field(
        ..., ge=0, description="Number of recent credit inquiries"
    )
    debt_ratio: float = Field(
        ..., ge=0, le=1, description="Current debt-to-income ratio"
    )


class RiskAssessmentResponse(BaseModel):
    risk_score: float = Field(..., ge=0, le=1, description="Risk score between 0 and 1")
    confidence: float = Field(
        ..., ge=0, le=1, description="Confidence in the risk assessment"
    )
    explanation: str = Field(..., description="Explanation of the risk assessment")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PolicyAssessment(BaseModel):
    decision: str = Field(..., description="Policy decision (APPROVE/REVIEW/DECLINE)")
    risk_grade: str = Field(..., description="Risk grade (A-E)")
    interest_rate: float = Field(..., ge=0, description="Recommended interest rate")
    recommended_max_amount: Optional[float] = Field(
        None, description="Recommended maximum loan amount"
    )
    rationale: str = Field(..., description="Rationale for the decision")
    conditions: List[str] = Field(
        default_factory=list, description="List of conditions applied"
    )
    policy_version: str = Field(..., description="Policy version used")


class RiskFactor(BaseModel):
    factor_name: str = Field(..., description="Name of the risk factor")
    severity: float = Field(..., ge=0, le=1, description="Severity of the risk factor")
    explanation: str = Field(..., description="Explanation of the risk factor")


class FraudRingMember(BaseModel):
    index: int = Field(..., description="Index of the member in the original dataset")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score of the member")
    anomaly_score: float = Field(..., ge=0, description="Anomaly score of the member")
    shared_neighbor_count: int = Field(
        ..., ge=0, description="Number of shared neighbors"
    )


class FraudRingResponse(BaseModel):
    ring_id: str = Field(..., description="Unique identifier for the fraud ring")
    members: List[FraudRingMember] = Field(
        ..., description="List of members in the fraud ring"
    )
    avg_risk_score: float = Field(
        ..., ge=0, le=1, description="Average risk score of the ring"
    )
    avg_anomaly_score: float = Field(
        ..., ge=0, description="Average anomaly score of the ring"
    )
    cohesiveness: float = Field(..., ge=0, le=1, description="Cohesiveness of the ring")
    risk_factors: List[str] = Field(..., description="List of risk factors identified")


class ApplicantScoreResponse(BaseModel):
    applicant_id: str = Field(..., description="Unique identifier for the applicant")
    enhanced_risk_score: float = Field(
        ..., ge=0, le=1, description="Enhanced risk score"
    )
    base_neighbor_risk: float = Field(
        ..., ge=0, le=1, description="Base neighbor risk score"
    )
    weighted_neighbor_risk: float = Field(
        ..., ge=0, le=1, description="Weighted neighbor risk score"
    )
    default_neighbor_ratio: float = Field(
        ..., ge=0, le=1, description="Default neighbor ratio"
    )
    anomaly_score: float = Field(..., ge=0, description="Anomaly score")
    fraud_indicator: Dict[str, Any] = Field(..., description="Fraud indicator details")
    risk_level: str = Field(..., description="Risk level (high/medium/low)")
    neighbor_stats: Dict[str, Any] = Field(..., description="Neighbor statistics")


class ScanStatusResponse(BaseModel):
    last_scan_time: Optional[str] = Field(
        None, description="Timestamp of the last scan"
    )
    is_scanning: bool = Field(
        ..., description="Whether a scan is currently in progress"
    )
    scan_interval_minutes: int = Field(
        ..., description="Interval between scans in minutes"
    )
    fraud_rings_detected: int = Field(..., description="Number of fraud rings detected")
    faiss_index_size: int = Field(..., description="Size of the FAISS index")


class RGCNFeaturesResponse(BaseModel):
    features: List[float] = Field(..., description="RGCN-generated features")
    feature_names: List[str] = Field(..., description="Names of the generated features")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the features")


class ScoreRequest(BaseModel):
    applicant_data: Dict[str, Any] = Field(
        ..., description="Applicant data for scoring"
    )
    k: int = Field(20, ge=1, description="Number of nearest neighbors to consider")


class ScoreResult(BaseModel):
    score: float = Field(..., ge=0, le=1, description="Final risk score")
    explanation: str = Field(..., description="Explanation of the score")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Health status (healthy/unhealthy)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(..., description="Additional health check details")


class PolicyDecisionRequest(BaseModel):
    risk_score: float = Field(..., ge=0, le=1, description="ML risk score")
    monthly_income: float = Field(0.0, ge=0, description="Monthly income")
    debt_ratio: float = Field(0.0, ge=0, le=1, description="Debt ratio")
    employment_months: int = Field(0, ge=0, description="Employment months")
    recent_inquiries: int = Field(0, ge=0, description="Recent inquiries")
    requested_amount: Optional[float] = Field(None, description="Requested loan amount")


class PolicyDecisionResponse(BaseModel):
    decision: str = Field(..., description="Policy decision")
    risk_grade: str = Field(..., description="Risk grade")
    interest_rate: float = Field(..., ge=0, description="Interest rate")
    recommended_max_amount: Optional[float] = Field(
        None, description="Recommended max amount"
    )
    rationale: str = Field(..., description="Rationale")
    conditions: List[str] = Field(
        default_factory=list, description="Conditions applied"
    )
    policy_version: str = Field(..., description="Policy version")


class CreditReportSignals(BaseModel):
    credit_score: float = Field(..., ge=0, le=1000, description="Credit score")
    credit_utilization: float = Field(
        ..., ge=0, le=1, description="Credit utilization ratio"
    )
    late_payments: int = Field(..., ge=0, description="Number of late payments")
    credit_age: float = Field(..., ge=0, description="Average age of credit accounts")


class FinancialStabilitySignals(BaseModel):
    dti_ratio: float = Field(..., ge=0, le=1, description="Debt-to-income ratio")
    savings_ratio: float = Field(..., ge=0, le=1, description="Savings-to-income ratio")
    employment_stability: float = Field(
        ..., ge=0, le=1, description="Employment stability score"
    )
    income_volatility: float = Field(
        ..., ge=0, le=1, description="Income volatility score"
    )


class StructuralProfile(BaseModel):
    network_density: float = Field(..., ge=0, le=1, description="Network density score")
    centrality_score: float = Field(..., ge=0, le=1, description="Centrality score")
    cluster_coefficient: float = Field(
        ..., ge=0, le=1, description="Cluster coefficient"
    )
    community_modularity: float = Field(
        ..., ge=0, le=1, description="Community modularity score"
    )


class RiskGrade(str):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class Decision(str):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    DECLINE = "DECLINE"


class PredictionRequest(BaseModel):
    """Request model for credit risk prediction."""

    applicant_id: str = Field(..., description="Unique identifier for the applicant")
    monthly_income: float = Field(..., ge=0, description="Monthly income in NGN")
    loan_amount: float = Field(..., ge=0, description="Requested loan amount in NGN")
    employment_months: int = Field(
        ..., ge=0, description="Months of employment stability"
    )
    recent_inquiries: int = Field(
        ..., ge=0, description="Number of recent credit inquiries"
    )
    debt_ratio: float = Field(
        ..., ge=0, le=1, description="Current debt-to-income ratio"
    )


class PredictionResponse(BaseModel):
    """Response model for credit risk prediction."""

    applicant_id: str = Field(..., description="Unique identifier for the applicant")
    risk_score: float = Field(..., ge=0, le=1, description="Risk score between 0 and 1")
    risk_grade: str = Field(..., description="Risk grade (A-E)")
    decision: str = Field(..., description="Policy decision (APPROVE/REVIEW/DECLINE)")
    interest_rate: float = Field(..., ge=0, description="Recommended interest rate")
    recommended_max_amount: Optional[float] = Field(
        None, description="Recommended maximum loan amount"
    )
    explanation: str = Field(..., description="Explanation of the decision")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchPredictionRequest(BaseModel):
    """Request model for batch credit risk prediction."""

    applicants: List[PredictionRequest] = Field(
        ..., description="List of applicant requests"
    )


class BatchPredictionResponse(BaseModel):
    """Response model for batch credit risk prediction."""

    predictions: List[PredictionResponse] = Field(
        ..., description="List of prediction responses"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FeatureImportance(BaseModel):
    """Model for feature importance."""

    feature_name: str = Field(..., description="Name of the feature")
    importance_score: float = Field(..., ge=0, le=1, description="Importance score")
    direction: str = Field(..., description="Direction of impact (positive/negative)")


class ModelMetadata(BaseModel):
    """Model metadata."""

    model_name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    training_date: datetime = Field(..., description="Date when the model was trained")
    accuracy: float = Field(..., ge=0, le=1, description="Accuracy of the model")
    f1_score: float = Field(..., ge=0, le=1, description="F1 score of the model")


class ModelEvaluation(BaseModel):
    """Model evaluation results."""

    accuracy: float = Field(..., ge=0, le=1, description="Accuracy")
    precision: float = Field(..., ge=0, le=1, description="Precision")
    recall: float = Field(..., ge=0, le=1, description="Recall")
    f1_score: float = Field(..., ge=0, le=1, description="F1 score")
    roc_auc: float = Field(..., ge=0, le=1, description="ROC AUC score")


class ModelTrainingConfig(BaseModel):
    """Model training configuration."""

    learning_rate: float = Field(..., ge=0, description="Learning rate")
    batch_size: int = Field(..., ge=1, description="Batch size")
    epochs: int = Field(..., ge=1, description="Number of epochs")
    validation_split: float = Field(..., ge=0, le=1, description="Validation split")


class ModelInferenceConfig(BaseModel):
    """Model inference configuration."""

    temperature: float = Field(..., ge=0, description="Temperature for inference")
    top_k: int = Field(..., ge=1, description="Top-k sampling")
    max_tokens: int = Field(..., ge=1, description="Maximum tokens for generation")


class ModelDeploymentConfig(BaseModel):
    """Model deployment configuration."""

    environment: str = Field(
        ..., description="Deployment environment (dev/staging/prod)"
    )
    instance_type: str = Field(..., description="Instance type for deployment")
    autoscaling_enabled: bool = Field(..., description="Whether autoscaling is enabled")
    min_instances: int = Field(..., ge=1, description="Minimum number of instances")
    max_instances: int = Field(..., ge=1, description="Maximum number of instances")


class ModelMonitoringConfig(BaseModel):
    """Model monitoring configuration."""

    drift_threshold: float = Field(..., ge=0, le=1, description="Drift threshold")
    performance_threshold: float = Field(
        ..., ge=0, le=1, description="Performance threshold"
    )
    alert_emails: List[str] = Field(..., description="Emails to alert on issues")


class ModelRegistryEntry(BaseModel):
    """Model registry entry."""

    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    author: str = Field(..., description="Author of the model")
    description: str = Field(..., description="Description of the model")
    tags: List[str] = Field(..., description="Tags for the model")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ModelArtifact(BaseModel):
    """Model artifact."""

    artifact_id: str = Field(..., description="Unique identifier for the artifact")
    model_id: str = Field(..., description="ID of the associated model")
    artifact_type: str = Field(
        ..., description="Type of artifact (model/weights/config)"
    )
    file_path: str = Field(..., description="File path of the artifact")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    checksum: str = Field(..., description="Checksum of the artifact")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelVersion(BaseModel):
    """Model version."""

    version_id: str = Field(..., description="Unique identifier for the version")
    model_id: str = Field(..., description="ID of the associated model")
    version_number: str = Field(..., description="Version number")
    description: str = Field(..., description="Description of the version")
    status: str = Field(..., description="Status of the version (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ModelDeployment(BaseModel):
    """Model deployment."""

    deployment_id: str = Field(..., description="Unique identifier for the deployment")
    model_id: str = Field(..., description="ID of the deployed model")
    version_id: str = Field(..., description="ID of the deployed version")
    environment: str = Field(..., description="Deployment environment")
    status: str = Field(..., description="Deployment status (running/failed/stopped)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ModelMonitoringAlert(BaseModel):
    """Model monitoring alert."""

    alert_id: str = Field(..., description="Unique identifier for the alert")
    model_id: str = Field(..., description="ID of the model")
    alert_type: str = Field(..., description="Type of alert (drift/performance)")
    severity: str = Field(..., description="Severity of the alert (low/medium/high)")
    message: str = Field(..., description="Alert message")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelDriftReport(BaseModel):
    """Model drift report."""

    report_id: str = Field(..., description="Unique identifier for the report")
    model_id: str = Field(..., description="ID of the model")
    drift_score: float = Field(..., ge=0, le=1, description="Drift score")
    drift_threshold: float = Field(..., ge=0, le=1, description="Drift threshold")
    drift_detected: bool = Field(..., description="Whether drift was detected")
    features_drifted: List[str] = Field(..., description="List of drifted features")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelPerformanceReport(BaseModel):
    """Model performance report."""

    report_id: str = Field(..., description="Unique identifier for the report")
    model_id: str = Field(..., description="ID of the model")
    performance_score: float = Field(..., ge=0, le=1, description="Performance score")
    performance_threshold: float = Field(
        ..., ge=0, le=1, description="Performance threshold"
    )
    performance_degraded: bool = Field(..., description="Whether performance degraded")
    metrics: Dict[str, float] = Field(..., description="Performance metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelExplainabilityReport(BaseModel):
    """Model explainability report."""

    report_id: str = Field(..., description="Unique identifier for the report")
    model_id: str = Field(..., description="ID of the model")
    explanation_method: str = Field(..., description="Explanation method used")
    feature_importance: List[FeatureImportance] = Field(
        ..., description="Feature importance scores"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelFairnessReport(BaseModel):
    """Model fairness report."""

    report_id: str = Field(..., description="Unique identifier for the report")
    model_id: str = Field(..., description="ID of the model")
    fairness_metrics: Dict[str, float] = Field(..., description="Fairness metrics")
    bias_detected: bool = Field(..., description="Whether bias was detected")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelRobustnessReport(BaseModel):
    """Model robustness report."""

    report_id: str = Field(..., description="Unique identifier for the report")
    model_id: str = Field(..., description="ID of the model")
    robustness_score: float = Field(..., ge=0, le=1, description="Robustness score")
    adversarial_examples: List[str] = Field(..., description="Adversarial examples")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelSecurityReport(BaseModel):
    """Model security report."""

    report_id: str = Field(..., description="Unique identifier for the report")
    model_id: str = Field(..., description="ID of the model")
    security_score: float = Field(..., ge=0, le=1, description="Security score")
    vulnerabilities: List[str] = Field(..., description="Security vulnerabilities")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelComplianceReport(BaseModel):
    """Model compliance report."""

    report_id: str = Field(..., description="Unique identifier for the report")
    model_id: str = Field(..., description="ID of the model")
    compliance_status: str = Field(
        ..., description="Compliance status (compliant/non-compliant)"
    )
    regulations: List[str] = Field(..., description="Regulations checked")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelAuditLog(BaseModel):
    """Model audit log."""

    log_id: str = Field(..., description="Unique identifier for the log")
    model_id: str = Field(..., description="ID of the model")
    action: str = Field(..., description="Action performed")
    actor: str = Field(..., description="Actor who performed the action")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModelLineage(BaseModel):
    """Model lineage."""

    lineage_id: str = Field(..., description="Unique identifier for the lineage")
    model_id: str = Field(..., description="ID of the model")
    parent_model_id: Optional[str] = Field(None, description="ID of the parent model")
    child_model_id: Optional[str] = Field(None, description="ID of the child model")
    relationship: str = Field(..., description="Relationship type")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelProvenance(BaseModel):
    """Model provenance."""

    provenance_id: str = Field(..., description="Unique identifier for the provenance")
    model_id: str = Field(..., description="ID of the model")
    data_source: str = Field(..., description="Data source used")
    preprocessing_steps: List[str] = Field(
        ..., description="Preprocessing steps applied"
    )
    training_algorithm: str = Field(..., description="Training algorithm used")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelGovernance(BaseModel):
    """Model governance."""

    governance_id: str = Field(..., description="Unique identifier for the governance")
    model_id: str = Field(..., description="ID of the model")
    owner: str = Field(..., description="Owner of the model")
    stewards: List[str] = Field(..., description="Stewards of the model")
    review_cycle: str = Field(..., description="Review cycle")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelLifecycle(BaseModel):
    """Model lifecycle."""

    lifecycle_id: str = Field(..., description="Unique identifier for the lifecycle")
    model_id: str = Field(..., description="ID of the model")
    phase: str = Field(
        ..., description="Current phase (development/testing/production)"
    )
    start_date: datetime = Field(..., description="Start date of the phase")
    end_date: Optional[datetime] = Field(None, description="End date of the phase")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModelMetadataExtended(BaseModel):
    """Extended model metadata."""

    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    author: str = Field(..., description="Author of the model")
    description: str = Field(..., description="Description of the model")
    tags: List[str] = Field(..., description="Tags for the model")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    lineage: Optional[ModelLineage] = Field(None, description="Model lineage")
    provenance: Optional[ModelProvenance] = Field(None, description="Model provenance")
    governance: Optional[ModelGovernance] = Field(None, description="Model governance")
    lifecycle: Optional[ModelLifecycle] = Field(None, description="Model lifecycle")


class ModelEvaluationExtended(BaseModel):
    """Extended model evaluation."""

    evaluation_id: str = Field(..., description="Unique identifier for the evaluation")
    model_id: str = Field(..., description="ID of the model")
    evaluation_type: str = Field(
        ..., description="Type of evaluation (accuracy/performance/fairness)"
    )
    metrics: Dict[str, float] = Field(..., description="Evaluation metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    report: Optional[
        Union[
            ModelPerformanceReport,
            ModelFairnessReport,
            ModelRobustnessReport,
            ModelSecurityReport,
            ModelComplianceReport,
        ]
    ] = Field(None, description="Evaluation report")


class ModelDeploymentExtended(BaseModel):
    """Extended model deployment."""

    deployment_id: str = Field(..., description="Unique identifier for the deployment")
    model_id: str = Field(..., description="ID of the deployed model")
    version_id: str = Field(..., description="ID of the deployed version")
    environment: str = Field(..., description="Deployment environment")
    status: str = Field(..., description="Deployment status (running/failed/stopped)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelDeploymentConfig] = Field(
        None, description="Deployment configuration"
    )
    monitoring: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )


class ModelMonitoringExtended(BaseModel):
    """Extended model monitoring."""

    monitoring_id: str = Field(..., description="Unique identifier for the monitoring")
    model_id: str = Field(..., description="ID of the model")
    status: str = Field(..., description="Monitoring status (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )
    alerts: List[ModelMonitoringAlert] = Field(..., description="Monitoring alerts")
    reports: List[
        Union[
            ModelDriftReport,
            ModelPerformanceReport,
            ModelExplainabilityReport,
            ModelFairnessReport,
            ModelRobustnessReport,
            ModelSecurityReport,
            ModelComplianceReport,
        ]
    ] = Field(..., description="Monitoring reports")


class ModelRegistryEntryExtended(BaseModel):
    """Extended model registry entry."""

    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    author: str = Field(..., description="Author of the model")
    description: str = Field(..., description="Description of the model")
    tags: List[str] = Field(..., description="Tags for the model")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )
    monitoring: Optional[ModelMonitoringExtended] = Field(
        None, description="Model monitoring"
    )


class ModelArtifactExtended(BaseModel):
    """Extended model artifact."""

    artifact_id: str = Field(..., description="Unique identifier for the artifact")
    model_id: str = Field(..., description="ID of the associated model")
    artifact_type: str = Field(
        ..., description="Type of artifact (model/weights/config)"
    )
    file_path: str = Field(..., description="File path of the artifact")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    checksum: str = Field(..., description="Checksum of the artifact")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )


class ModelVersionExtended(BaseModel):
    """Extended model version."""

    version_id: str = Field(..., description="Unique identifier for the version")
    model_id: str = Field(..., description="ID of the associated model")
    version_number: str = Field(..., description="Version number")
    description: str = Field(..., description="Description of the version")
    status: str = Field(..., description="Status of the version (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    artifacts: List[ModelArtifactExtended] = Field(..., description="Model artifacts")
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )
    monitoring: Optional[ModelMonitoringExtended] = Field(
        None, description="Model monitoring"
    )


class ModelDeploymentExtendedWithConfig(BaseModel):
    """Extended model deployment with configuration."""

    deployment_id: str = Field(..., description="Unique identifier for the deployment")
    model_id: str = Field(..., description="ID of the deployed model")
    version_id: str = Field(..., description="ID of the deployed version")
    environment: str = Field(..., description="Deployment environment")
    status: str = Field(..., description="Deployment status (running/failed/stopped)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelDeploymentConfig] = Field(
        None, description="Deployment configuration"
    )
    monitoring: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )


class ModelMonitoringExtendedWithConfig(BaseModel):
    """Extended model monitoring with configuration."""

    monitoring_id: str = Field(..., description="Unique identifier for the monitoring")
    model_id: str = Field(..., description="ID of the model")
    status: str = Field(..., description="Monitoring status (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )
    alerts: List[ModelMonitoringAlert] = Field(..., description="Monitoring alerts")
    reports: List[
        Union[
            ModelDriftReport,
            ModelPerformanceReport,
            ModelExplainabilityReport,
            ModelFairnessReport,
            ModelRobustnessReport,
            ModelSecurityReport,
            ModelComplianceReport,
        ]
    ] = Field(..., description="Monitoring reports")
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )


class ModelRegistryEntryExtendedWithMetadata(BaseModel):
    """Extended model registry entry with metadata."""

    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    author: str = Field(..., description="Author of the model")
    description: str = Field(..., description="Description of the model")
    tags: List[str] = Field(..., description="Tags for the model")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )
    monitoring: Optional[ModelMonitoringExtended] = Field(
        None, description="Model monitoring"
    )


class ModelArtifactExtendedWithMetadata(BaseModel):
    """Extended model artifact with metadata."""

    artifact_id: str = Field(..., description="Unique identifier for the artifact")
    model_id: str = Field(..., description="ID of the associated model")
    artifact_type: str = Field(
        ..., description="Type of artifact (model/weights/config)"
    )
    file_path: str = Field(..., description="File path of the artifact")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    checksum: str = Field(..., description="Checksum of the artifact")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )


class ModelVersionExtendedWithMetadata(BaseModel):
    """Extended model version with metadata."""

    version_id: str = Field(..., description="Unique identifier for the version")
    model_id: str = Field(..., description="ID of the associated model")
    version_number: str = Field(..., description="Version number")
    description: str = Field(..., description="Description of the version")
    status: str = Field(..., description="Status of the version (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    artifacts: List[ModelArtifactExtended] = Field(..., description="Model artifacts")
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )
    monitoring: Optional[ModelMonitoringExtended] = Field(
        None, description="Model monitoring"
    )


class ModelDeploymentExtendedWithConfigAndMetadata(BaseModel):
    """Extended model deployment with configuration and metadata."""

    deployment_id: str = Field(..., description="Unique identifier for the deployment")
    model_id: str = Field(..., description="ID of the deployed model")
    version_id: str = Field(..., description="ID of the deployed version")
    environment: str = Field(..., description="Deployment environment")
    status: str = Field(..., description="Deployment status (running/failed/stopped)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelDeploymentConfig] = Field(
        None, description="Deployment configuration"
    )
    monitoring: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )


class ModelMonitoringExtendedWithConfigAndMetadata(BaseModel):
    """Extended model monitoring with configuration and metadata."""

    monitoring_id: str = Field(..., description="Unique identifier for the monitoring")
    model_id: str = Field(..., description="ID of the model")
    status: str = Field(..., description="Monitoring status (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )
    alerts: List[ModelMonitoringAlert] = Field(..., description="Monitoring alerts")
    reports: List[
        Union[
            ModelDriftReport,
            ModelPerformanceReport,
            ModelExplainabilityReport,
            ModelFairnessReport,
            ModelRobustnessReport,
            ModelSecurityReport,
            ModelComplianceReport,
        ]
    ] = Field(..., description="Monitoring reports")
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )


class ModelRegistryEntryExtendedWithMetadataAndEvaluations(BaseModel):
    """Extended model registry entry with metadata and evaluations."""

    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    author: str = Field(..., description="Author of the model")
    description: str = Field(..., description="Description of the model")
    tags: List[str] = Field(..., description="Tags for the model")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )
    monitoring: Optional[ModelMonitoringExtended] = Field(
        None, description="Model monitoring"
    )


class ModelArtifactExtendedWithMetadataAndEvaluations(BaseModel):
    """Extended model artifact with metadata and evaluations."""

    artifact_id: str = Field(..., description="Unique identifier for the artifact")
    model_id: str = Field(..., description="ID of the associated model")
    artifact_type: str = Field(
        ..., description="Type of artifact (model/weights/config)"
    )
    file_path: str = Field(..., description="File path of the artifact")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    checksum: str = Field(..., description="Checksum of the artifact")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )


class ModelVersionExtendedWithMetadataAndEvaluations(BaseModel):
    """Extended model version with metadata and evaluations."""

    version_id: str = Field(..., description="Unique identifier for the version")
    model_id: str = Field(..., description="ID of the associated model")
    version_number: str = Field(..., description="Version number")
    description: str = Field(..., description="Description of the version")
    status: str = Field(..., description="Status of the version (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    artifacts: List[ModelArtifactExtended] = Field(..., description="Model artifacts")
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )
    monitoring: Optional[ModelMonitoringExtended] = Field(
        None, description="Model monitoring"
    )


class ModelDeploymentExtendedWithConfigAndMetadataAndEvaluations(BaseModel):
    """Extended model deployment with configuration, metadata, and evaluations."""

    deployment_id: str = Field(..., description="Unique identifier for the deployment")
    model_id: str = Field(..., description="ID of the deployed model")
    version_id: str = Field(..., description="ID of the deployed version")
    environment: str = Field(..., description="Deployment environment")
    status: str = Field(..., description="Deployment status (running/failed/stopped)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelDeploymentConfig] = Field(
        None, description="Deployment configuration"
    )
    monitoring: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )


class ModelMonitoringExtendedWithConfigAndMetadataAndEvaluations(BaseModel):
    """Extended model monitoring with configuration, metadata, and evaluations."""

    monitoring_id: str = Field(..., description="Unique identifier for the monitoring")
    model_id: str = Field(..., description="ID of the model")
    status: str = Field(..., description="Monitoring status (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )
    alerts: List[ModelMonitoringAlert] = Field(..., description="Monitoring alerts")
    reports: List[
        Union[
            ModelDriftReport,
            ModelPerformanceReport,
            ModelExplainabilityReport,
            ModelFairnessReport,
            ModelRobustnessReport,
            ModelSecurityReport,
            ModelComplianceReport,
        ]
    ] = Field(..., description="Monitoring reports")
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )


class ModelRegistryEntryExtendedWithMetadataAndEvaluationsAndDeployments(BaseModel):
    """Extended model registry entry with metadata, evaluations, and deployments."""

    model_id: str = Field(..., description="Unique identifier for the model")
    model_name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    author: str = Field(..., description="Author of the model")
    description: str = Field(..., description="Description of the model")
    tags: List[str] = Field(..., description="Tags for the model")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )
    monitoring: Optional[ModelMonitoringExtended] = Field(
        None, description="Model monitoring"
    )


class ModelArtifactExtendedWithMetadataAndEvaluationsAndDeployments(BaseModel):
    """Extended model artifact with metadata, evaluations, and deployments."""

    artifact_id: str = Field(..., description="Unique identifier for the artifact")
    model_id: str = Field(..., description="ID of the associated model")
    artifact_type: str = Field(
        ..., description="Type of artifact (model/weights/config)"
    )
    file_path: str = Field(..., description="File path of the artifact")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    checksum: str = Field(..., description="Checksum of the artifact")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )


class ModelVersionExtendedWithMetadataAndEvaluationsAndDeployments(BaseModel):
    """Extended model version with metadata, evaluations, and deployments."""

    version_id: str = Field(..., description="Unique identifier for the version")
    model_id: str = Field(..., description="ID of the associated model")
    version_number: str = Field(..., description="Version number")
    description: str = Field(..., description="Description of the version")
    status: str = Field(..., description="Status of the version (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    artifacts: List[ModelArtifactExtended] = Field(..., description="Model artifacts")
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )
    monitoring: Optional[ModelMonitoringExtended] = Field(
        None, description="Model monitoring"
    )


class ModelDeploymentExtendedWithConfigAndMetadataAndEvaluationsAndDeployments(
    BaseModel
):
    """Extended model deployment with configuration, metadata, evaluations, and deployments."""

    deployment_id: str = Field(..., description="Unique identifier for the deployment")
    model_id: str = Field(..., description="ID of the deployed model")
    version_id: str = Field(..., description="ID of the deployed version")
    environment: str = Field(..., description="Deployment environment")
    status: str = Field(..., description="Deployment status (running/failed/stopped)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelDeploymentConfig] = Field(
        None, description="Deployment configuration"
    )
    monitoring: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )


class ModelMonitoringExtendedWithConfigAndMetadataAndEvaluationsAndDeployments(
    BaseModel
):
    """Extended model monitoring with configuration, metadata, evaluations, and deployments."""

    monitoring_id: str = Field(..., description="Unique identifier for the monitoring")
    model_id: str = Field(..., description="ID of the model")
    status: str = Field(..., description="Monitoring status (active/inactive)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Optional[ModelMonitoringConfig] = Field(
        None, description="Monitoring configuration"
    )
    alerts: List[ModelMonitoringAlert] = Field(..., description="Monitoring alerts")
    reports: List[
        Union[
            ModelDriftReport,
            ModelPerformanceReport,
            ModelExplainabilityReport,
            ModelFairnessReport,
            ModelRobustnessReport,
            ModelSecurityReport,
            ModelComplianceReport,
        ]
    ] = Field(..., description="Monitoring reports")
    metadata: Optional[ModelMetadataExtended] = Field(
        None, description="Extended metadata"
    )
    evaluations: List[ModelEvaluationExtended] = Field(
        ..., description="Model evaluations"
    )
    deployments: List[ModelDeploymentExtended] = Field(
        ..., description="Model deployments"
    )


# Report Generator Models
class ReportRequest(BaseModel):
    """Request model for report generation."""

    applicant_name: str = Field(..., description="Name of the applicant")
    score: float = Field(..., ge=0, le=1, description="Credit score")
    risk_level: str = Field(..., description="Risk level (high/medium/low)")
    decision: str = Field(..., description="Decision (APPROVE/REVIEW/DECLINE)")


class ReportResponse(BaseModel):
    """Response model for report generation request."""

    report_id: str = Field(..., description="Unique identifier for the report")
    status: str = Field(..., description="Status of the report generation")


class ReportStatusResponse(BaseModel):
    """Response model for report status."""

    report_id: str = Field(..., description="Unique identifier for the report")
    status: str = Field(..., description="Status of the report")
    content: Optional[str] = Field(None, description="Report content")
    created_at: str = Field(..., description="Creation timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
