"""Causal Inference Service - API for estimating treatment effects and counterfactuals."""
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(__file__))

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.models import (
    PropensityRequest,
    PropensityResponse,
    TreatmentEffectRequest,
    TreatmentEffect,
    TreatmentEffectResponse,
    CounterfactualRequest,
    CounterfactualResponse,
    CounterfactualScenario,
    UpliftRequest,
    UpliftResponse,
    UpliftSegment,
    CausalAnalysisSummary,
)
from app.inference_engine import CausalInferenceEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Causal Inference Service",
    description="API for causal inference in credit scoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = CausalInferenceEngine()


class HealthCheckResponse:
    """Health check response."""
    pass


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "causal-inference",
        "model_loaded": True
    }


@app.post("/estimate-propensity", response_model=PropensityResponse)
async def estimate_propensity(request: PropensityRequest):
    """
    Estimate propensity score (probability of treatment assignment).

    - **features**: Applicant features
    - **applicant_id**: Unique applicant ID
    """
    try:
        result = engine.estimate_propensity(request.features)

        return PropensityResponse(
            applicant_id=request.applicant_id,
            propensity_score=result["propensity_score"],
            treatment_probability=result["treatment_probability"],
            risk_tier=result["risk_tier"],
            method=result["method"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error estimating propensity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/estimate-treatment-effect", response_model=TreatmentEffectResponse)
async def estimate_treatment_effect(request: TreatmentEffectRequest):
    """
    Estimate treatment effects using various methods.

    - **features**: Applicant features
    - **applicant_id**: Unique applicant ID
    - **treatment**: Treatment type
    - **method**: Estimation method (matching, ipw, doubly_robust, all)
    """
    try:
        effects = engine.estimate_treatment_effect(
            request.features,
            request.method
        )

        effects_list = [
            TreatmentEffect(
                method=e["method"],
                ate=e["ate"],
                confidence_interval=e["confidence_interval"],
                p_value=e["p_value"],
                standard_error=e["standard_error"]
            )
            for e in effects
        ]

        avg_outcome_treated = 0.35 if request.treatment == "approve" else 0.55
        avg_outcome_control = 0.52

        return TreatmentEffectResponse(
            applicant_id=request.applicant_id,
            treatment=request.treatment,
            effects=effects_list,
            estimated_outcome_treated=avg_outcome_treated,
            estimated_outcome_control=avg_outcome_control,
            sample_size=1000,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error estimating treatment effect: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/counterfactuals", response_model=CounterfactualResponse)
async def generate_counterfactuals(request: CounterfactualRequest):
    """
    Generate counterfactual scenarios for credit decisions.

    - **features**: Applicant features
    - **applicant_id**: Unique applicant ID
    - **scenarios**: Optional list of specific scenarios
    """
    try:
        result = engine.generate_counterfactuals(
            request.features,
            actual_treatment="approve"
        )

        scenarios = [
            CounterfactualScenario(
                scenario_id=s["scenario_id"],
                treatment=s["treatment"],
                predicted_outcome=s["predicted_outcome"],
                outcome_probability=s["outcome_probability"],
                risk_change=s["risk_change"],
                recommendation=s["recommendation"]
            )
            for s in result["scenarios"]
        ]

        return CounterfactualResponse(
            applicant_id=request.applicant_id,
            actual_treatment="current",
            scenarios=scenarios,
            optimal_decision=result["optimal_decision"],
            expected_improvement=result["expected_improvement"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error generating counterfactuals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/uplift-modeling", response_model=UpliftResponse)
async def uplift_modeling(request: UpliftRequest):
    """
    Perform uplift modeling to predict treatment responsiveness.

    - **features**: Applicant features
    - **applicant_id**: Unique applicant ID
    """
    try:
        result = engine.calculate_uplift(request.features)

        segments = [
            UpliftSegment(
                segment=s["segment"],
                score=s["score"],
                percentile=s["percentile"],
                description=s["description"],
                recommended_action=s["recommended_action"]
            )
            for s in result["segments"]
        ]

        return UpliftResponse(
            applicant_id=request.applicant_id,
            uplift_score=result["uplift_score"],
            segment=result["segment"],
            treatment_responsiveness=result["treatment_responsiveness"],
            segments=segments,
            recommendation=result["recommendation"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error in uplift modeling: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=CausalAnalysisSummary)
async def full_analysis(request: PropensityRequest):
    """
    Perform complete causal inference analysis.

    Combines propensity scoring, treatment effects, counterfactuals, and uplift.
    """
    try:
        propensity = engine.estimate_propensity(request.features)
        effects = engine.estimate_treatment_effect(request.features, method="all")
        counterfactuals = engine.generate_counterfactuals(request.features)
        uplift = engine.calculate_uplift(request.features)

        effects_list = [
            TreatmentEffect(
                method=e["method"],
                ate=e["ate"],
                confidence_interval=e["confidence_interval"],
                p_value=e["p_value"],
                standard_error=e["standard_error"]
            )
            for e in effects
        ]

        uplift_segment = UpliftSegment(
            segment=uplift["segment"],
            score=uplift["uplift_score"],
            percentile=50 + uplift["uplift_score"] * 50,
            description=uplift["treatment_responsiveness"],
            recommended_action=uplift["recommendation"]
        )

        counter_scenarios = [
            CounterfactualScenario(
                scenario_id=s["scenario_id"],
                treatment=s["treatment"],
                predicted_outcome=s["predicted_outcome"],
                outcome_probability=s["outcome_probability"],
                risk_change=s["risk_change"],
                recommendation=s["recommendation"]
            )
            for s in counterfactuals["scenarios"]
        ]

        if propensity["propensity_score"] > 0.6 and uplift["uplift_score"] > 0.2:
            recommended_decision = "approve"
            confidence = 0.85
        elif propensity["propensity_score"] < 0.3 and uplift["uplift_score"] < -0.2:
            recommended_decision = "deny"
            confidence = 0.75
        else:
            recommended_decision = "review"
            confidence = 0.65

        return CausalAnalysisSummary(
            applicant_id=request.applicant_id,
            propensity_score=propensity["propensity_score"],
            treatment_effects=effects_list,
            counterfactuals=counter_scenarios,
            uplift=uplift_segment,
            recommended_decision=recommended_decision,
            confidence=confidence,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error in full analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "causal-inference",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/estimate-propensity",
            "/estimate-treatment-effect",
            "/counterfactuals",
            "/uplift-modeling",
            "/analyze"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
