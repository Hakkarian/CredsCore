"""Simplified Unified Augmented Credit Scoring Service."""
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.dirname(__file__))

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.inference_engine import AugmentedScoringEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Augmented Credit Scoring",
    description="ML + Causal Inference + Social Capital",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = AugmentedScoringEngine()

# Known credit feature keys — if any appear at the request top level,
# the caller sent flat features (e.g. gateway proxy) instead of wrapped.
CREDIT_FEATURE_KEYS = {
    "RevolvingUtilizationOfUnsecuredLines", "age",
    "NumberOfTime30_59DaysPastDueNotWorse", "DebtRatio", "MonthlyIncome",
    "NumberOfOpenCreditLinesAndLoans", "NumberOfTimes90DaysLate",
    "NumberRealEstateLoansOrLines", "NumberOfTime60_89DaysPastDueNotWorse",
    "NumberOfDependents",
}


def _extract_features(request: Dict[str, Any]) -> Dict[str, Any]:
    """Extract features from request, handling both flat and wrapped formats."""
    features = request.get("features", {}) or {}
    # If features dict is empty but credit keys exist at top level, merge them
    if not features:
        flat = {k: v for k, v in request.items() if k in CREDIT_FEATURE_KEYS}
        if flat:
            features = flat
    return features


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/combined")
@app.post("/combined-score")
@app.post("/predict-enhanced")
async def get_combined_score(request: Dict[str, Any]):
    """Alias endpoints for combined augmented score (routed via gateway)."""
    return await get_score(request)


@app.post("/score")
async def get_score(request: Dict[str, Any]):
    """
    Get unified augmented credit score.

    Combines ML prediction + Causal inference + Social capital.
    """
    try:
        features = _extract_features(request)
        applicant_id = request.get("applicant_id", "unknown")
        entity_id = request.get("entity_id", applicant_id)

        result = engine.calculate_combined_score(
            applicant_id=applicant_id,
            features=features,
            entity_id=entity_id,
            include_causal=True,
            include_social=True
        )

        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insights")
async def get_insights(request: Dict[str, Any]):
    """
    Get unified insights combining causal and social analysis.

    Simplified single endpoint for the insights tab.
    """
    try:
        features = _extract_features(request)
        applicant_id = request.get("applicant_id", "unknown")
        entity_id = request.get("entity_id", applicant_id)

        # Get ML score
        ml_score = engine.predict_ml(features)

        # Get causal insights
        causal = engine._calculate_causal(features)

        # Get social insights - pass features for feature-aware calculation
        social = engine.social.calculate_social_capital(entity_id, features)

        # Combined recommendation — the authoritative final decision. Computed
        # once here so the "recommendation" field and the summary line stay in
        # sync (previously the summary reported causal['recommendation'], which
        # could contradict the combined recommendation shown on the same card).
        combined_recommendation = _combine_recommendation(
            ml_score["risk_level"],
            causal["recommendation"],
            social["risk_indicators"]
        )

        # Create unified insights
        return {
            "applicant_id": applicant_id,
            "timestamp": datetime.utcnow().isoformat(),

            # Overall score
            "ml_risk": ml_score["default_probability"],
            "ml_risk_level": ml_score["risk_level"],

            # Causal insights (simplified)
            "propensity_score": causal["propensity_score"]["score"],
            "causal_recommendation": causal["recommendation"],
            "optimal_decision": causal["optimal_decision"],
            "expected_improvement": causal["expected_improvement"],
            "counterfactuals": [
                {
                    "decision": cf["treatment"],
                    "probability": cf["outcome_probability"],
                    "change": cf["risk_change"]
                }
                for cf in causal["counterfactuals"][:3]
            ],

            # Social insights (simplified)
            "social_trust": social["scores"]["trust"],
            "social_influence": social["scores"]["influence"],
            "social_network_size": social["network_size"],
            "social_connections": social["connection_count"],
            "fraud_risk": social["risk_indicators"]["fraud_risk"],
            "social_credit_score": social["social_credit_score"],

            # Combined recommendation
            "recommendation": combined_recommendation,
            "confidence": causal["confidence"],

            # Human readable summary
            "summary": _generate_summary(ml_score, causal, social, combined_recommendation)
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/network/{entity_id}")
async def get_network(entity_id: str, depth: int = 2):
    """Get network visualization data."""
    try:
        data = engine.social.get_network_data(entity_id, depth)
        return data
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {
        "service": "augmented-scoring",
        "version": "2.0.0",
        "endpoints": ["/health", "/score", "/combined", "/combined-score", "/predict-enhanced", "/insights", "/network/{id}", "/agents/analyze", "/agents/report/{applicant_id}"]
    }


@app.post("/agents/analyze")
async def agentic_analysis(request: Dict[str, Any]):
    """
    Multi-agent credit risk analysis based on CreditXAI architecture.

    Agents: BRA, FRA, GRA, CRA, CAA, SSA
    """
    try:
        features = _extract_features(request)
        applicant_id = request.get("applicant_id", "unknown")
        entity_id = request.get("entity_id", applicant_id)
        include_history = request.get("include_history", True)

        # Get base ML score (BRA + FRA combined)
        ml_score = engine.predict_ml(features)

        # Governance Risk Analysis (GRA)
        governance = engine.social.calculate_social_capital(entity_id, features)
        governance_risk = governance["risk_indicators"]

        # Causal inference (additional financial analysis)
        causal = engine._calculate_causal(features)

        # Business Risk Agent (BRA) — behavioral / credit-conduct risk
        business_risk = engine.calculate_behavioral_risk(features)

        # Financial Risk Agent (FRA) — financial capacity / solvency risk
        financial_risk = engine.calculate_financial_risk(features)

        # Comprehensive Rating Agent (CRA) — weighted combination of distinct scores
        composite_risk = business_risk * 0.4 + financial_risk * 0.6

        # Chief Analyst Agent (CAA) - final consensus
        risk_factors = [
            ml_score["risk_level"],
            causal["propensity_score"]["tier"],
            "low" if governance_risk["fraud_risk"] < 0.3 else "medium" if governance_risk["fraud_risk"] < 0.6 else "high"
        ]

        # Count occurrences
        risk_counts = {}
        for rf in risk_factors:
            risk_counts[rf] = risk_counts.get(rf, 0) + 1

        # CAA consensus decision
        if "high" in risk_counts and risk_counts["high"] >= 2:
            caa_decision = "deny"
            caa_confidence = 0.85
        elif "low" in risk_counts and risk_counts["low"] >= 2:
            caa_decision = "approve"
            caa_confidence = 0.90
        else:
            caa_decision = "review"
            caa_confidence = 0.70

        # System Supervisory Agent (SSA) - quality checks
        agent_outputs = {
            "bra": {"risk_score": business_risk, "weight": 0.4, "domain": "behavioral"},
            "fra": {"risk_score": financial_risk, "weight": 0.6, "domain": "financial"},
            "gra": {"governance_score": governance["scores"]["trust"], "risk_level": governance_risk},
            "cra": {"composite_score": composite_risk},
            "caa": {"decision": caa_decision, "confidence": caa_confidence}
        }

        ssa_validation = _ssa_validate_outputs(agent_outputs)

        return {
            "applicant_id": applicant_id,
            "timestamp": datetime.utcnow().isoformat(),

            # Agent Analysis Layer
            "agents": {
                "bra": {
                    "agent": "Business Risk Analysis",
                    "risk_score": business_risk,
                    "risk_level": ml_score["risk_level"],
                    "analysis": f"Business risk factors show {ml_score['risk_level']} risk profile"
                },
                "fra": {
                    "agent": "Financial Risk Analysis",
                    "risk_score": financial_risk,
                    "financial_health": _assess_financial_health(financial_risk),
                    "key_metrics": _extract_key_metrics(features)
                },
                "gra": {
                    "agent": "Governance Risk Analysis",
                    "trust_score": governance["scores"]["trust"],
                    "fraud_risk": governance_risk["fraud_risk"],
                    "reputational_risk": governance_risk["reputational_risk"],
                    "network_connections": governance["connection_count"]
                },
                "cra": {
                    "agent": "Comprehensive Rating",
                    "composite_score": composite_risk,
                    "rating": _calculate_rating(composite_risk),
                    "method": "weighted_average"
                }
            },

            # Decision Layer
            "caa": {
                "agent": "Chief Analyst",
                "consensus_decision": caa_decision,
                "confidence": caa_confidence,
                "risk_consensus": risk_factors,
                "rationale": f"Consensus of {risk_counts.get('low', 0)} low, {risk_counts.get('medium', 0)} medium, {risk_counts.get('high', 0)} high risk signals"
            },

            # Supervisory Layer
            "ssa": {
                "agent": "System Supervisory",
                "validation_passed": ssa_validation["passed"],
                "quality_score": ssa_validation["score"],
                "traceability": ssa_validation["trace"],
                "anomalies_detected": ssa_validation.get("anomalies", [])
            },

            # Enhanced metrics
            "history_aware": include_history,
            "causal_insights": {
                "propensity_tier": causal["propensity_score"]["tier"],
                "optimal_decision": causal["optimal_decision"],
                "counterfactuals_count": len(causal["counterfactuals"])
            },

            # Final recommendation
            "recommendation": caa_decision,
            "confidence": caa_confidence,
            "combined_risk_score": composite_risk
        }
    except Exception as e:
        logger.error(f"Error in agentic analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/report/{applicant_id}")
async def get_agent_report(applicant_id: str, request: Dict[str, Any]):
    """
    Rating Report Writing Agent (RRA) - generates structured credit report.
    Takes the agentic_analysis result and formats it into a professional report.
    """
    try:
        features = _extract_features(request)
        analysis = request.get("analysis", {})

        # Extract agent data
        agents = analysis.get("agents", {})
        caa = analysis.get("caa", {})
        cra = agents.get("cra", {})
        bra = agents.get("bra", {})
        fra = agents.get("fra", {})
        gra = agents.get("gra", {})

        # Map rating to outlook
        rating = cra.get("rating", "BBB")
        consensus = caa.get("consensus_decision", "review")

        if rating in ["AAA", "AA"]:
            outlook = "positive"
        elif rating in ["A", "BBB"]:
            outlook = "stable"
        else:
            outlook = "negative"

        # Generate dynamic key factors based on scores
        key_factors = []

        # BRA factor
        bra_risk = bra.get("risk_score", 0.5)
        if bra_risk < 0.2:
            key_factors.append("Strong business risk profile with stable revenue indicators")
        elif bra_risk > 0.6:
            key_factors.append("Elevated business risk requiring close monitoring")
        else:
            key_factors.append("Moderate business risk with stable indicators")

        # FRA factor
        if "excellent" in (fra.get("financial_health") or ""):
            key_factors.append("Excellent financial health with strong debt-to-income management")
        elif "poor" in (fra.get("financial_health") or ""):
            key_factors.append("Financial stress indicators suggest caution")
        else:
            key_factors.append("Financial metrics show moderate stability")

        # GRA factor
        fraud_risk = gra.get("fraud_risk", 0)
        if fraud_risk < 0.1:
            key_factors.append(
                f"Social capital indicates trustworthy network with {gra.get('network_connections', 0)} verified connections")
        elif fraud_risk > 0.2:
            key_factors.append("Elevated governance risk due to network factors")
        else:
            key_factors.append("Social network connections show typical trust patterns")

        # Causal factor
        causal = analysis.get("causal_insights", {})
        propensity = causal.get("propensity_tier", "medium")
        if propensity == "low":
            key_factors.append("Causal analysis indicates strong propensity for repayment")
        elif propensity == "high":
            key_factors.append("Counterfactual analysis suggests considering alternative decisions")

        # Build dynamic report
        report = {
            "report_id": f"RPT-{applicant_id}-{datetime.utcnow().strftime('%Y%m%d')}",
            "generated_at": datetime.utcnow().isoformat(),
            "applicant_id": applicant_id,

            "executive_summary": {
                "rating": rating,
                "outlook": outlook,
                "recommendation": consensus,
                "key_factors": key_factors[:4]  # Top 4 factors
            },

            "risk_assessment": {
                "business_risk": _describe_business_risk(bra),
                "financial_risk": _describe_financial_risk(fra),
                "governance_risk": _describe_governance_risk(gra)
            },

            "agent_consensus": {
                "bra_score": bra.get("risk_score", 0),
                "fra_score": fra.get("risk_score", 0),
                # Governance has no single risk_score in the analyze response;
                # derive the same 0-1 governance risk the agent-grid uses
                # (avg of fraud_risk/0.3 and reputational_risk/0.2) so the
                # consensus block agrees with the grid instead of showing a
                # trust*weight value that isn't comparable.
                "gra_score": (
                    min(1.0, gra.get("fraud_risk", 0) / 0.3)
                    + min(1.0, gra.get("reputational_risk", 0) / 0.2)
                ) / 2,
                "caa_decision": consensus
            },

            "methodology": "Multi-agent consensus-based CreditXAI methodology",
            "confidence_level": f"{caa.get('confidence', 0.7) * 100:.0f}%",
              "risk_breakdown": {
                "ml_weight": analysis.get("feature_weights", {}).get("ml_weight", 0.6),
                "causal_weight": analysis.get("feature_weights", {}).get("causal_weight", 0.1),
                "social_weight": analysis.get("feature_weights", {}).get("social_weight", 0.3)
            },
            "combined_risk_score": analysis.get("combined_risk_score", 0.5)
        }

        return report
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _describe_business_risk(bra: Dict) -> str:
    """Generate business risk description."""
    score = bra.get("risk_score", 0.5)
    level = bra.get("risk_level", "medium")
    if score < 0.2:
        return f"Low - Business risk factors show {level} risk profile with stable revenue indicators"
    elif score > 0.6:
        return f"High - Business risk factors show {level} risk profile requiring close monitoring"
    return f"Medium - Business risk factors show {level} risk profile with mixed indicators"


def _describe_financial_risk(fra: Dict) -> str:
    """Generate financial risk description."""
    health = fra.get("financial_health", "fair")
    score = fra.get("risk_score", 0.3)

    if health == "excellent":
        return "Low - Excellent financial health with strong debt-to-income management"
    elif health == "good":
        return "Low to Medium - Good financial health with minor risk indicators"
    elif health == "poor":
        return "High - Financial stress indicators suggest caution required"
    return f"Medium - {health.capitalize()} financial health with moderate risk factors"


def _describe_governance_risk(gra: Dict) -> str:
    """Generate governance risk description."""
    trust = gra.get("trust_score", 0.7)
    fraud = gra.get("fraud_risk", 0.15)
    connections = gra.get("network_connections", 20)

    if trust > 0.8 and fraud < 0.1:
        return f"Low - High trust score ({trust:.0%}) with {connections} verified network connections"
    elif fraud > 0.2:
        return f"High - Elevated fraud risk ({fraud:.0%}) detected in network analysis"
    return f"Medium - Trust score {trust:.0%} with typical network patterns ({connections} connections)"


def _assess_financial_health(financial_risk: float) -> str:
    """Assess financial health from the FRA risk score.

    The FRA score (calculate_financial_risk) already weights debt burden
    (40%), income adequacy (35%), and credit-line leverage (25%) into a
    0..1 value where higher = worse financial health. Map that score to a
    label so the displayed health stays consistent with the
    decision-driving score and actually reflects income.

    Previously this re-thresholded raw features on utilization alone and
    only checked income in the narrow "excellent" tier, so a high-income
    applicant with high utilization was always labeled "poor" regardless
    of income.
    """
    if financial_risk < 0.30:
        return "excellent"
    elif financial_risk < 0.50:
        return "good"
    elif financial_risk < 0.70:
        return "fair"
    else:
        return "poor"


def _extract_key_metrics(features: Dict[str, float]) -> Dict[str, Any]:
    """Extract key financial metrics."""
    return {
        "revolving_utilization": f"{features.get('RevolvingUtilizationOfUnsecuredLines', 0.5):.1%}",
        "debt_ratio": f"{features.get('DebtRatio', 0.3):.1%}",
        "monthly_income": f"${features.get('MonthlyIncome', 5000):,.0f}",
        "age": int(features.get("age", 35)),
        "late_payments_90d": int(features.get("NumberOfTimes90DaysLate", 0)),
        "open_credit_lines": int(features.get("NumberOfOpenCreditLinesAndLoans", 5))
    }


def _calculate_rating(risk_score: float) -> str:
    """Calculate credit rating."""
    if risk_score < 0.2:
        return "AAA"
    elif risk_score < 0.3:
        return "AA"
    elif risk_score < 0.4:
        return "A"
    elif risk_score < 0.5:
        return "BBB"
    elif risk_score < 0.6:
        return "BB"
    elif risk_score < 0.7:
        return "B"
    else:
        return "CCC"


def _ssa_validate_outputs(agent_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """System Supervisory Agent validation.

    Quality gate over agent outputs: range integrity, score consistency,
    and consensus coherence. Validation fails when outputs fall outside
    [0,1], when risk scores diverge beyond a tolerable threshold, or when
    the CAA decision contradicts the evidence — it is not a rubber stamp.
    """
    validation = {
        "passed": True,
        "score": 0.95,
        "trace": [],
        "anomalies": []
    }

    # Range integrity + collect comparable 0-1 risk scores (BRA, FRA, CRA).
    risk_scores: Dict[str, float] = {}
    for key in ("bra", "fra", "cra"):
        out = agent_outputs.get(key, {})
        score = out.get("risk_score", out.get("composite_score"))
        if score is None:
            continue
        if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
            validation["anomalies"].append(f"{key.upper()} score out of [0,1] range: {score}")
            validation["score"] -= 0.3
            continue
        risk_scores[key] = float(score)

    # Consensus coherence: CAA decision must not contradict the evidence.
    caa = agent_outputs.get("caa", {})
    decision = caa.get("decision")
    if risk_scores and decision:
        avg_risk = sum(risk_scores.values()) / len(risk_scores)
        if decision == "approve" and avg_risk >= 0.6:
            validation["anomalies"].append(f"CAA 'approve' contradicts high average risk {avg_risk:.2f}")
            validation["score"] -= 0.3
        elif decision == "deny" and avg_risk < 0.3:
            validation["anomalies"].append(f"CAA 'deny' contradicts low average risk {avg_risk:.2f}")
            validation["score"] -= 0.3

    # Score consistency: high variance across agents signals disagreement.
    if len(risk_scores) >= 2:
        avg_score = sum(risk_scores.values()) / len(risk_scores)
        variance = sum((s - avg_score) ** 2 for s in risk_scores.values()) / len(risk_scores)
        if variance > 0.1:
            validation["anomalies"].append(f"High variance in risk scores: {variance:.2f}")
            validation["score"] -= 0.2

    validation["trace"] = [
        f"{k}: {v.get('decision', v.get('risk_score', v.get('composite_score', 'N/A')))}"
        for k, v in agent_outputs.items()
    ]
    validation["score"] = max(0.0, validation["score"])
    validation["passed"] = validation["score"] >= 0.7 and not validation["anomalies"]

    return validation


def _combine_recommendation(ml_level: str, causal_rec: str, risks: Dict) -> str:
    """Combine all signals into final recommendation."""
    social_risk = (risks["fraud_risk"] + risks["default_risk"]) / 2

    if ml_level == "high" or social_risk > 0.6:
        return "deny"
    elif ml_level == "low" and causal_rec == "approve" and social_risk < 0.3:
        return "approve"
    else:
        return "review"


def _generate_summary(ml: Dict, causal: Dict, social: Dict, final_recommendation: str) -> str:
    """Generate human-readable summary."""
    parts = []

    # ML summary
    parts.append(f"ML model predicts {ml['risk_level']} risk ({ml['default_probability']:.0%}) - {ml['prediction']}")

    # Causal summary
    parts.append(f"Propensity score: {causal['propensity_score']['score']:.0%} ({causal['propensity_score']['tier']} risk)")

    # Social summary
    parts.append(f"Social trust: {social['scores']['trust']:.0%} with {social['connection_count']} connections")

    # Combined — use the authoritative combined recommendation so the summary
    # never contradicts the Recommendation field on the same card.
    parts.append(f"Final recommendation: {final_recommendation}")

    return ". ".join(parts)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
