import sys
import os
import json

shared_path = os.path.join(os.path.dirname(__file__), "..", "..", "shared")
sys.path.insert(0, shared_path)

# Ensure the service root is in sys.path for absolute imports
service_root = os.path.join(os.path.dirname(__file__), "..")
if service_root not in sys.path:
    sys.path.insert(0, service_root)

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

import httpx
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from app.predictor import predict_risk_score, batch_predict_risk_scores, get_predictor
# from app.rgcn.predictor import predict_rgcn_features  # Temporarily disabled
from credscore_shared.models import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    # RGCNFeaturesResponse,  # Temporarily disabled
    HealthCheckResponse,
    PolicyDecisionRequest,
)
from credscore_shared.config import ServiceConfig
from credscore_shared.client import ServiceClient


class ClientApplicantData(BaseModel):
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


class RiskFactor(BaseModel):
    feature: str
    shap_value: float
    impact: str


class ClientPredictionResult(BaseModel):
    prediction: int
    default_probability: float
    risk_level: str
    message: str
    top_risk_factors: List[RiskFactor]
    # TEMPORARY demo shim transparency: bounded income-monotonicity correction
    # applied to default_probability. 0.0 when DEMO_MONOTONIC_FIX is off. Remove
    # after the #1 monotone_constraints retrain.
    monotonic_correction: float = 0.0


class SimilarApplicantData(BaseModel):
    similar_indices: List[int]
    distances: List[float]
    default_labels: List[int]
    default_count: int
    total_similar: int
    default_rate: float
    risk_assessment: str


class SimilarApplicantsResponse(BaseModel):
    applicant: ClientApplicantData
    similar_applicants: SimilarApplicantData
    interpretation: Dict[str, str]
    human_explanation: str


class ExplainDenialResponse(BaseModel):
    prediction: str
    default_probability: float
    denial_reasons: List[RiskFactor]
    similar_approved_applicants: Dict[str, Any]
    explanation: str
    recommendation: str
    human_explanation: str


class ThinFileResult(BaseModel):
    base_prediction: Dict[str, float]
    neighbor_features: Dict[str, float]
    enhanced_prediction: Dict[str, float]
    interpretation: Dict[str, Any]
    human_explanation: str


class DriftResult(BaseModel):
    drift_analysis: Dict[str, Any]
    interpretation: Dict[str, str]
    human_explanation: str


class PeerGroupsResult(BaseModel):
    total_customers: int
    n_segments: int
    segments: List[Dict[str, Any]]
    summary: Dict[str, Any]
    human_explanation: str


class CausalInferenceResult(BaseModel):
    applicant_id: str
    propensity_score: float
    recommended_decision: str
    confidence: float
    treatment_effects: List[Dict[str, Any]]
    counterfactuals: List[Dict[str, Any]]


class SocialCapitalResult(BaseModel):
    entity_id: str
    entity_type: str
    social_credit_score: float
    network_size: int
    connection_count: int
    risk_indicators: Dict[str, float]
    analysis_summary: str


class CombinedScoreResult(BaseModel):
    applicant_id: str
    ml_probability: float
    ml_risk_level: str
    causal_recommendation: str
    causal_confidence: float
    social_credit_score: float
    social_risk_indicator: float
    combined_probability: float
    combined_risk_level: str
    explanation: str


class PredictWithFeaturesRequest(BaseModel):
    applicant_data: ClientApplicantData
    include_causal: bool = True
    include_social: bool = True
    applicant_id: str = ""


POLICY_SERVICE_URL = os.getenv("POLICY_SERVICE_URL", "http://localhost:8003")
FRAUD_SERVICE_URL = os.getenv("FRAUD_SERVICE_URL", "http://fraud-detection:8000")
CAUSAL_SERVICE_URL = os.getenv("CAUSAL_SERVICE_URL", "http://localhost:8006")
SOCIAL_SERVICE_URL = os.getenv("SOCIAL_SERVICE_URL", "http://localhost:8009")

# Service Clients
clients: Dict[str, ServiceClient] = {}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Credit Scoring Service",
    description="AI-powered credit risk scoring API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "details": {"service": "credit-scoring", "uptime": "running"},
    }


# Score endpoint for orchestrator
@app.post("/score")
async def score(request: Dict[str, Any]):
    applicant_data = request.get("applicant", {})
    use_rgcn = request.get("use_rgcn", True)

    # Extract features from ClientData for the predictor
    # Mapping ClientData (shared) to predictor features
    # Since predictor.predict handles mapping via to_dataframe,
    # we just need to pass the dict.

    predictor = get_predictor()

    ML_FEATURE_KEYS = [
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

    # If the applicant payload already contains ML features, use them directly.
    has_ml_features = all(k in applicant_data for k in ML_FEATURE_KEYS)
    if has_ml_features:
        features = {k: applicant_data[k] for k in ML_FEATURE_KEYS}
    else:
        # Derive what we can from ClientData (credit_score 0-1000)
        credit_score = applicant_data.get("credit_score", 500)
        utilization_proxy = round(1.0 - credit_score / 1000.0, 3)
        features = {
            "RevolvingUtilizationOfUnsecuredLines": utilization_proxy,
            "age": 30,
            "NumberOfTime30_59DaysPastDueNotWorse": 0,
            "DebtRatio": utilization_proxy,
            "MonthlyIncome": 5000.0,
            "NumberOfOpenCreditLinesAndLoans": 5,
            "NumberOfTimes90DaysLate": 0,
            "NumberRealEstateLoansOrLines": 0,
            "NumberOfTime60_89DaysPastDueNotWorse": 0,
            "NumberOfDependents": 0,
        }

    result = predictor.predict(features, use_rgcn=use_rgcn)
    return {"base_probability": result["default_probability"]}


# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        logger.info(
            f"Processing prediction request for applicant {request.applicant_id}"
        )

        # Get risk score from ML model
        risk_score = await predict_risk_score(request)

        # Get RGCN features (temporarily disabled)
        # rgcn_features_response = await predict_rgcn_features(request)

        # Apply policy decision via HTTP call
        policy_request = PolicyDecisionRequest(
            risk_score=risk_score,
            monthly_income=request.monthly_income,
            debt_ratio=request.debt_ratio,
            employment_months=request.employment_months,
            recent_inquiries=request.recent_inquiries,
            requested_amount=request.loan_amount,
        )

        policy_result = await clients["policy"].post(
            "evaluate", json=policy_request.model_dump()
        )

        # Construct final response
        response = PredictionResponse(
            applicant_id=request.applicant_id,
            risk_score=risk_score,
            risk_grade=policy_result["risk_grade"],
            decision=policy_result["decision"],
            interest_rate=policy_result["interest_rate"],
            recommended_max_amount=policy_result["recommended_max_amount"],
            explanation=policy_result["rationale"],
        )

        logger.info(
            f"Prediction completed for applicant {request.applicant_id}: {response.decision}"
        )
        return response

    except httpx.HTTPError as e:
        logger.error(
            f"HTTP error calling policy service for applicant {request.applicant_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=503, detail=f"Policy service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(
            f"Error processing prediction for applicant {request.applicant_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# Batch prediction endpoint
@app.post("/batch-predict", response_model=BatchPredictionResponse)
async def batch_predict(request: BatchPredictionRequest) -> BatchPredictionResponse:
    try:
        logger.info(
            f"Processing batch prediction request for {len(request.applicants)} applicants"
        )

        predictions = await batch_predict_risk_scores(request.applicants)

        response = BatchPredictionResponse(predictions=predictions)

        logger.info(
            f"Batch prediction completed for {len(request.applicants)} applicants"
        )
        return response

    except Exception as e:
        logger.error(f"Error processing batch prediction: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Batch prediction failed: {str(e)}"
        )


# RGCN feature extraction endpoint (temporarily disabled)
# @app.post("/rgcn-features", response_model=RGCNFeaturesResponse)
# async def rgcn_features(request: PredictionRequest) -> RGCNFeaturesResponse:
#     try:
#         logger.info(f"Extracting RGCN features for applicant {request.applicant_id}")
#
#         response = await predict_rgcn_features(request)
#
#         logger.info(f"RGCN features extracted for applicant {request.applicant_id}")
#         return response
#
#     except Exception as e:
#         logger.error(
#             f"Error extracting RGCN features for applicant {request.applicant_id}: {e}",
#             exc_info=True,
#         )
#         raise HTTPException(
#             status_code=500, detail=f"RGCN feature extraction failed: {str(e)}"
#         )


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Credit Scoring Service",
        "endpoints": ["/health", "/predict", "/batch-predict", "/rgcn-features"],
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/client-predict", response_model=ClientPredictionResult)
async def client_predict(data: ClientApplicantData):
    predictor = get_predictor()
    result = predictor.predict(data.dict(), use_rgcn=True)
    return ClientPredictionResult(
        prediction=result["prediction"],
        default_probability=result["default_probability"],
        risk_level=result["risk_level"],
        message=result["message"],
        monotonic_correction=result.get("monotonic_correction", 0.0),
        top_risk_factors=[
            RiskFactor(
                feature=rf["feature"], shap_value=rf["shap_value"], impact=rf["impact"]
            )
            for rf in result["risk_factors"]
        ],
    )


@app.post("/similar-applicants")
async def similar_applicants(data: ClientApplicantData, k: int = 10):
    from .similar import SimilarFinder

    finder = SimilarFinder()
    import sys

    # Write to a temp file instead of stderr
    with open("debug.log", "a") as f:
        f.write(f"finder.features={finder.features is not None}\n")
        f.write(f"feature_names={finder.feature_names[:3]}\n")
        f.write(f"labels={finder.labels is not None}\n")

    result = finder.find_similar(data.dict(), k)

    with open("debug.log", "a") as f:
        f.write(f"result default_rate={result['similar_applicants']['default_rate']}\n")

    return result


@app.post("/explain-denial")
async def explain_denial(data: ClientApplicantData, k: int = 20):
    predictor = get_predictor()
    from .explain import explain_denial_reason

    return explain_denial_reason(data.dict(), k)


@app.post("/thin-file-predict")
async def thin_file_predict(data: ClientApplicantData, k: int = 5):
    predictor = get_predictor()
    from .thinfile import predict_thin_file

    return predict_thin_file(data.dict(), k)


@app.post("/monitor-drift")
async def monitor_drift(request: Request, n_clusters: int = 10):
    """Monitor model drift for batch of applicants."""
    from .drift import monitor_model_drift
    try:
        # Read raw body and parse JSON manually
        body = await request.body()
        data = json.loads(body)
        logger.info(f"monitor-drift received {len(data)} records, n_clusters={n_clusters}")

        result = monitor_model_drift(data, n_clusters)
        return result
    except Exception as e:
        import traceback
        logger.error(f"Error in monitor_drift endpoint: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "drift_analysis": {
                    "error": str(e),
                    "drift_level": "error",
                    "drift_detected": False,
                },
                "interpretation": {
                    "drift_level": "error",
                    "recommendation": f"Server error during analysis: {str(e)}",
                },
                "human_explanation": f"Drift analysis failed with error: {str(e)}",
            }
        )


@app.post("/peer-groups")
async def peer_groups(request: Request, n_clusters: int = 5):
    """Segment customers into peer groups."""
    from .peers import segment_peer_groups
    try:
        # Read raw body and parse JSON manually
        body = await request.body()
        data = json.loads(body)
        logger.info(f"peer-groups received {len(data)} records, n_clusters={n_clusters}")

        result = segment_peer_groups(data, n_clusters)
        return result
    except Exception as e:
        import traceback
        logger.error(f"Error in peer_groups endpoint: {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "total_customers": 0,
                "n_segments": 0,
                "segments": [],
                "summary": {"highest_risk_segment": None, "lowest_risk_segment": None, "balanced_clustering": False, "model_quality": "error"},
                "human_explanation": f"Peer group analysis failed: {str(e)}",
            }
        )


@app.get("/model-info")
async def model_info():
    predictor = get_predictor()
    return predictor.get_model_info()


# Background task for periodic fraud ring scanning
# NOTE: Fraud detection should be triggered via its HTTP API, not direct import
# The fraud-detection service should expose a /scan endpoint for this purpose


async def run_fraud_scan():
    """Background task for periodic fraud ring scanning via HTTP."""
    is_docker = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"
    if not is_docker:
        logger.info("Fraud scan disabled - not running in Docker")
        return

    while True:
        try:
            result = await clients["fraud"].get("fraud-rings/status")
            logger.info(
                f"Fraud scan status: {result.get('fraud_rings_detected', 0)} rings detected"
            )
        except Exception as e:
            logger.warning(f"Fraud scan check failed: {e}")

        await asyncio.sleep(3600)


# === Causal Inference Integration Endpoints ===

@app.post("/causal-analysis/{applicant_id}", response_model=CausalInferenceResult)
async def causal_analysis(applicant_id: str, data: ClientApplicantData):
    """Get causal inference analysis for an applicant by calling causal inference service."""
    try:
        features = data.dict()

        result = await clients["causal"].post(
            "analyze",
            json={"applicant_id": applicant_id, "features": features}
        )

        return CausalInferenceResult(
            applicant_id=result.get("applicant_id", applicant_id),
            propensity_score=result.get("propensity_score", 0.0),
            recommended_decision=result.get("recommended_decision", "review"),
            confidence=result.get("confidence", 0.5),
            treatment_effects=result.get("treatment_effects", []),
            counterfactuals=result.get("counterfactuals", []),
        )
    except Exception as e:
        logger.error(f"Causal analysis failed for {applicant_id}: {e}")
        raise HTTPException(status_code=503, detail=f"Causal service unavailable: {str(e)}")


@app.post("/social-score/{applicant_id}", response_model=SocialCapitalResult)
async def social_score(applicant_id: str, data: Dict[str, Any] = {}):
    """Get social capital score for an applicant by calling social capital service."""
    try:
        result = await clients["social"].post(
            "calculate",
            json={"applicant_id": applicant_id, **data}
        )

        scores = result.get("scores", {})
        risk = result.get("risk_indicators", {})

        # Calculate a credit-score-like social score (300-850 range)
        social_credit_score = 300 + (
            scores.get("trust", 0) * 200 +
            scores.get("influence", 0) * 150 +
            scores.get("centrality", 0) * 100 +
            scores.get("engagement", 0) * 100
        )

        return SocialCapitalResult(
            entity_id=result.get("entity_id", applicant_id),
            entity_type=result.get("entity_type", "individual"),
            social_credit_score=min(850, social_credit_score),
            network_size=result.get("network_size", 0),
            connection_count=result.get("connection_count", 0),
            risk_indicators=risk,
            analysis_summary=result.get("analysis_summary", ""),
        )
    except Exception as e:
        logger.error(f"Social score failed for {applicant_id}: {e}")
        raise HTTPException(status_code=503, detail=f"Social service unavailable: {str(e)}")


@app.post("/combined-score", response_model=CombinedScoreResult)
async def combined_score(request: PredictWithFeaturesRequest):
    """Combined prediction using ML + Causal + Social features."""
    try:
        predictor = get_predictor()
        applicant_id = request.applicant_id or f"app_{random.randint(10000, 99999)}"

        # Get ML prediction
        ml_result = predictor.predict(request.applicant_data.dict(), use_rgcn=True)
        ml_probability = ml_result["default_probability"]
        ml_risk_level = ml_result["risk_level"]

        # Get causal analysis if enabled
        causal_recommendation = "none"
        causal_confidence = 0.0
        if request.include_causal:
            try:
                causal_result = await clients["causal"].post(
                    "analyze",
                    json={"applicant_id": applicant_id, "features": request.applicant_data.dict()}
                )
                causal_recommendation = causal_result.get("recommended_decision", "review")
                causal_confidence = causal_result.get("confidence", 0.5)
            except Exception as e:
                logger.warning(f"Causal analysis skipped: {e}")

        # Get social score if enabled
        social_credit_score = 500.0
        social_risk = 0.5
        if request.include_social:
            try:
                social_result = await clients["social"].post(
                    "calculate",
                    json={"applicant_id": applicant_id}
                )
                scores = social_result.get("scores", {})
                social_credit_score = 300 + (
                    scores.get("trust", 0) * 200 +
                    scores.get("influence", 0) * 150 +
                    scores.get("centrality", 0) * 100
                )
                risk_indicators = social_result.get("risk_indicators", {})
                social_risk = risk_indicators.get("fraud_risk", 0.5) * 0.5 + risk_indicators.get("default_risk", 0.5) * 0.5
            except Exception as e:
                logger.warning(f"Social analysis skipped: {e}")

        # Combine scores
        # ML probability weighted by confidence
        # Social score: higher = better, convert to risk contribution
        social_risk_contribution = (850 - social_credit_score) / 550 * 0.3  # Normalize

        # Causal insight adjustment
        causal_adjustment = 0.0
        if causal_recommendation == "approve":
            causal_adjustment = -0.05 * causal_confidence
        elif causal_recommendation == "deny":
            causal_adjustment = 0.05 * causal_confidence

        combined_probability = (
            ml_probability * 0.6 +
            social_risk_contribution * 0.2 +
            social_risk * 0.2
        ) + causal_adjustment

        combined_probability = max(0.0, min(1.0, combined_probability))

        if combined_probability < 0.3:
            combined_risk_level = "low"
        elif combined_probability < 0.6:
            combined_risk_level = "medium"
        else:
            combined_risk_level = "high"

        explanation = (
            f"Combined score: ML probability {ml_probability:.2%}, "
            f"social credit score {social_credit_score:.0f}, "
            f"causal recommendation: {causal_recommendation} "
            f"(confidence: {causal_confidence:.0%})"
        )

        return CombinedScoreResult(
            applicant_id=applicant_id,
            ml_probability=ml_probability,
            ml_risk_level=ml_risk_level,
            causal_recommendation=causal_recommendation,
            causal_confidence=causal_confidence,
            social_credit_score=social_credit_score,
            social_risk_indicator=social_risk,
            combined_probability=combined_probability,
            combined_risk_level=combined_risk_level,
            explanation=explanation,
        )
    except Exception as e:
        logger.error(f"Combined score failed: {e}")
        raise HTTPException(status_code=500, detail=f"Combined prediction failed: {str(e)}")


# Modify existing predict endpoint to optionally include social/causal
@app.post("/predict-enhanced")
async def predict_enhanced(request: PredictWithFeaturesRequest):
    """Enhanced prediction endpoint with optional causal and social features."""
    return await combined_score(request)


@app.on_event("startup")
async def startup_event():
    clients["policy"] = ServiceClient(POLICY_SERVICE_URL)
    clients["fraud"] = ServiceClient(FRAUD_SERVICE_URL)
    clients["causal"] = ServiceClient(CAUSAL_SERVICE_URL)
    clients["social"] = ServiceClient(SOCIAL_SERVICE_URL)
    asyncio.create_task(run_fraud_scan())
    logger.info("Credit scoring service started with background fraud monitoring and causal/social clients")


@app.on_event("shutdown")
async def shutdown_event():
    for client in clients.values():
        await client.close()
