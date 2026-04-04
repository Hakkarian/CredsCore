from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from app.models import ClientData, CreditApplicationRequest, RiskAssessmentResponse, PolicyAssessment
from app.policy import assess_risk
from app.transforms import safe_log
from app.faiss_index import FAISSCreditIndex

app = FastAPI(title="Credit Risk Prediction API", description="Production-grade credit risk system with ML estimation + policy decision engine", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

model, explainer, feature_names, faiss_index_val = None, None, None, None

FEATURE_MAP = {
    'RevolvingUtilizationOfUnsecuredLines': 'RevolvingUtilizationOfUnsecuredLines', 'age': 'age',
    'NumberOfTime30_59DaysPastDueNotWorse': 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio': 'DebtRatio',
    'MonthlyIncome': 'MonthlyIncome', 'NumberOfOpenCreditLinesAndLoans': 'NumberOfOpenCreditLinesAndLoans',
    'NumberOfTimes90DaysLate': 'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines': 'NumberRealEstateLoansOrLines',
    'NumberOfTime60_89DaysPastDueNotWorse': 'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents': 'NumberOfDependents'
}

def load_models():
    global model, explainer, feature_names, faiss_index_val
    md = os.path.join(os.path.dirname(__file__), 'app', 'saved_models')
    model = joblib.load(os.path.join(md, 'lightgbm_credit_model.pkl'))
    explainer = joblib.load(os.path.join(md, 'shap_explainer.pkl'))
    feature_names = joblib.load(os.path.join(md, 'feature_names.pkl'))
    faiss_index_val = FAISSCreditIndex()
    faiss_index_val.load_index(md)

@app.on_event("startup")
async def startup():
    load_models()

@app.get("/")
def root():
    return {"message": "Credit Risk Prediction API", "version": "3.0.0", "design": "ML Risk Estimation + Policy Decision Engine", "endpoints": {"/health": "Health check", "/predict": "Predict (POST)", "/assess": "Full risk assessment with policy (POST)", "/policy-info": "Policy configuration", "/similar-applicants": "Similar applicants (POST)", "/explain-denial": "Explain denial (POST)", "/thin-file-predict": "Thin-file prediction (POST)", "/monitor-drift": "Monitor drift (POST)", "/peer-groups": "Peer groups (POST)"}}

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None, "faiss_loaded": faiss_index_val is not None}

@app.get("/model-info")
def info():
    return {"model_type": "LightGBM + FAISS", "features_count": len(feature_names) or 0, "features": feature_names or [], "faiss_size": faiss_index_val.index.ntotal if faiss_index_val and faiss_index_val.index else 0}

def to_dataframe(cd: ClientData):
    data = {tn: getattr(cd, fn) for fn, tn in FEATURE_MAP.items()}
    df = pd.DataFrame([data])
    for f in feature_names:
        if f not in df.columns:
            df[f] = 0
    return df.reindex(columns=feature_names, fill_value=0)

def get_shap(shap_vals):
    return shap_vals[1] if isinstance(shap_vals, list) and len(shap_vals) == 2 else shap_vals

@app.post("/predict")
def predict(cd: ClientData):
    try:
        df = to_dataframe(cd)
        prob = float(model.predict(df)[0])
        sv = get_shap(explainer.shap_values(df))
        vals = sv.flatten()
        idx = np.argsort(np.abs(vals))[::-1][:5]
        factors = [{"feature": feature_names[i], "shap_value": float(vals[i]), "impact": "increases_risk" if vals[i] > 0 else "decreases_risk"} for i in idx]
        return {"prediction": 1 if prob > 0.5 else 0, "default_probability": prob, "risk_level": "high" if prob > 0.5 else "medium" if prob > 0.3 else "low", "message": "High risk - declined" if prob > 0.5 else "Low risk - approved", "top_risk_factors": factors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/similar-applicants")
def similar(cd: ClientData, k: int = 10):
    try:
        df = to_dataframe(cd)
        result = faiss_index_val.find_similar_applicants(df, k=k)
        rate = result['default_rate'] * 100
        msg = f"Out of {result['total_similar']} similar past applicants, {result['default_count']} defaulted ({rate:.0f}%). " + ("This is concerning - nearly half had trouble paying back." if rate > 40 else "This is higher than average - some risk here." if rate > 20 else "This looks good - most similar borrowers paid back.")
        return {"applicant": cd.dict(), "similar_applicants": result, "interpretation": {"default_rate": f"{rate:.1f}%", "risk_assessment": result['risk_assessment'], "summary": f"{result['default_count']}/{result['total_similar']} defaulted"}, "human_explanation": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain-denial")
def explain_denial(cd: ClientData, k: int = 20):
    try:
        df = to_dataframe(cd)
        prob = float(model.predict(df)[0])
        sv = get_shap(explainer.shap_values(df))
        result = faiss_index_val.explain_denial_with_similar_approved(df, sv, feature_names, k=k)
        reasons = [f['feature'] for f in result['top_risk_factors'][:3]]
        detail = [{"index": ce['index'], "distance": ce['distance'], "features": {n: float(faiss_index_val.training_data[ce['index']][i]) for i, n in enumerate(feature_names)} if faiss_index_val.training_data is not None else {}} for ce in result['counter_examples'][:3]]
        msg = f"Applicant flagged with {prob*100:.0f}% default risk. Reasons: {', '.join(reasons)}. Found {result['similar_approved_count']} similar approved applicants."
        return {"prediction": "denied", "default_probability": prob, "denial_reasons": result['top_risk_factors'], "similar_approved_applicants": {"count": result['similar_approved_count'], "counter_examples": detail}, "explanation": result['explanation'], "human_explanation": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/thin-file-predict")
def thin_file(cd: ClientData, k: int = 5):
    try:
        df = to_dataframe(cd)
        base = float(model.predict(df)[0])
        ni = faiss_index_val.get_neighbor_features(df, k=k)
        nr = ni['weighted_neighbor_risk']
        dc = 1.0 / (1.0 + ni['avg_neighbor_distance'])
        nw = min(0.3, dc * 0.5)
        enhanced = base * (1 - nw) + nr * nw
        change_note = f"Similar customers had {nr*100:.1f}% default rate, adjusted from {base*100:.1f}% to {enhanced*100:.1f}%. " if abs(base - enhanced) > 0.005 else f"Similar customers had {nr*100:.1f}% default rate, confirming {enhanced*100:.1f}%. "
        msg = f"Base model predicts {base*100:.1f}% risk. " + change_note + ("Limited credit history - neighbor data helps validate." if ni['avg_neighbor_distance'] > 2.0 else "Enough data for confident prediction.")
        return {"base_prediction": {"probability": base, "prediction": 1 if base > 0.5 else 0}, "neighbor_features": ni, "enhanced_prediction": {"probability": float(enhanced), "prediction": 1 if enhanced > 0.5 else 0, "neighbor_weight_applied": float(nw)}, "interpretation": {"thin_file_detected": ni['avg_neighbor_distance'] > 2.0, "neighbor_risk_level": "high" if nr > 0.3 else "medium" if nr > 0.1 else "low"}, "human_explanation": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitor-drift")
def drift(new_data: List[Dict[str, Any]], n_clusters: int = 10):
    try:
        df = pd.DataFrame(new_data)
        for f in feature_names:
            if f not in df.columns:
                df[f] = 0
        df = df.reindex(columns=feature_names, fill_value=0)
        result = faiss_index_val.monitor_drift(df, n_clusters=n_clusters)
        kl = result['kl_divergence']
        rec = "Model retraining recommended" if result['drift_level'] == 'high' else "Monitor closely" if result['drift_level'] == 'medium' else "No action needed"
        msg = f"Compared recent applicants against training data. " + (f"Applicants look different (drift: {kl:.2f}). Retraining recommended." if result['drift_level'] == 'high' else f"Some difference detected (drift: {kl:.2f}). Consider retraining soon." if result['drift_level'] == 'medium' else f"Applicants look similar (drift: {kl:.2f}). Predictions remain reliable.")
        return {"drift_analysis": result, "interpretation": {"drift_detected": result['drift_detected'], "drift_level": result['drift_level'], "kl_divergence": f"{kl:.4f}", "recommendation": rec}, "human_explanation": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/peer-groups")
def peers(data: List[Dict[str, Any]], n_clusters: int = 5):
    try:
        df = pd.DataFrame(data)
        for f in feature_names:
            if f not in df.columns:
                df[f] = 0
        df = df.reindex(columns=feature_names, fill_value=0)
        cr = faiss_index_val.cluster_customers(df, n_clusters=n_clusters)
        segments = [{"segment": f"Group {c['cluster_id'] + 1}", "size": c['size'], "percentage": f"{c['percentage']:.1f}%", "default_rate": f"{c['default_rate']*100:.1f}%" if c['default_rate'] is not None else "N/A", "risk_level": "High Risk" if c['default_rate'] and c['default_rate'] > 0.3 else "Medium Risk" if c['default_rate'] and c['default_rate'] > 0.1 else "Low Risk" if c['default_rate'] is not None else "Unknown", "profile": c['centroid']} for c in cr['clusters']]
        with_rate = [s for s in segments if s['default_rate'] != 'N/A']
        highest = max(with_rate, key=lambda x: float(x['default_rate'].strip('%'))) if with_rate else None
        lowest = min(with_rate, key=lambda x: float(x['default_rate'].strip('%'))) if with_rate else None
        msg = f"Grouped {cr['total_customers']:,} customers into {n_clusters} segments. " + (f"Highest-risk: {highest['segment']} ({highest['default_rate']}). Lowest-risk: {lowest['segment']} ({lowest['default_rate']})." if highest and lowest else "No default data available.")
        return {"total_customers": cr['total_customers'], "n_segments": n_clusters, "segments": segments, "summary": {"highest_risk_segment": highest['segment'] if highest else None, "lowest_risk_segment": lowest['segment'] if lowest else None}, "human_explanation": msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Enhanced Risk Assessment Endpoint (Layer 1 + Layer 2)
# Separates ML risk estimation from policy decision making
# ============================================================

@app.post("/assess", response_model=RiskAssessmentResponse)
def assess(application: CreditApplicationRequest):
    """
    Full risk assessment combining ML estimation (Layer 1) and policy decision (Layer 2).
    
    Layer 1: ML model estimates continuous risk probability
    Layer 2: Policy engine converts risk into approve/review/decline decision
    
    This separation enables:
    - Models can be retrained without changing policies
    - Policies can be updated for compliance without retraining
    - Full audit trail of both risk estimate and decision
    """
    try:
        # === LAYER 1: ML Risk Estimation ===
        cd = ClientData(**application.dict(exclude={"credit_report", "financial_stability", "structural_profile"}))
        df = to_dataframe(cd)
        
        # Apply log-space transformation to MonthlyIncome
        income_log = safe_log(application.MonthlyIncome)
        if "MonthlyIncome" in df.columns:
            df["MonthlyIncome"] = income_log
        
        risk_score = float(model.predict(df)[0])
        
        # Get SHAP explanations
        sv = get_shap(explainer.shap_values(df))
        vals = sv.flatten()
        idx = np.argsort(np.abs(vals))[::-1][:5]
        factors = [{"feature": feature_names[i], "shap_value": float(vals[i]), "impact": "increases_risk" if vals[i] > 0 else "decreases_risk"} for i in idx]
        
        # === LAYER 2: Policy Decision ===
        monthly_income = application.get_monthly_income()
        recent_inquiries = application.get_recent_inquiries()
        employment_tenure = application.get_employment_tenure()
        requested_amount = application.get_requested_amount()
        
        policy_result = assess_risk(
            risk_score=risk_score,
            monthly_income=monthly_income,
            debt_ratio=application.DebtRatio,
            employment_months=employment_tenure,
            recent_inquiries=recent_inquiries,
            requested_amount=requested_amount
        )
        
        # Build human-readable summaries
        grade = policy_result["risk_grade"]
        decision = policy_result["decision"]
        
        decision_messages = {
            "APPROVE": f"Approved with Grade {grade} credit profile.",
            "REVIEW": f"Requires manual review - Grade {grade} profile.",
            "DECLINE": f"Declined - Grade {grade} exceeds risk tolerance."
        }
        
        tier_message = decision_messages.get(decision, f"Grade {grade} - {decision}")
        
        income_str = f"₦{monthly_income:,.0f}" if monthly_income > 0 else "Not provided"
        max_str = f"₦{policy_result['recommended_max_amount']:,.0f}" if policy_result.get("recommended_max_amount") else "N/A"
        
        human_summary = (
            f"Risk score: {risk_score:.1%} | Grade {grade} | Decision: {decision}. "
            f"Monthly income: {income_str}. "
            f"Recommended max loan: {max_str} at {policy_result['interest_rate']}% interest. "
            f"{'Conditions: ' + '; '.join(policy_result['conditions']) if policy_result['conditions'] else ''}"
        )
        
        return RiskAssessmentResponse(
            risk_score=risk_score,
            default_probability=risk_score,
            top_risk_factors=factors,
            policy=PolicyAssessment(**policy_result),
            human_summary=human_summary,
            tier_message=tier_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/policy-info")
def policy_info():
    """Get information about the current policy configuration."""
    from app.policy import DEFAULT_TIERS, Decision, RiskGrade
    tiers = [
        {
            "grade": t.grade.value,
            "score_range": f"{t.min_score:.0%} - {t.max_score:.0%}",
            "decision": t.decision.value,
            "base_interest_rate": t.base_interest_rate,
            "max_debt_to_income": t.max_debt_to_income,
            "description": t.description
        }
        for t in DEFAULT_TIERS
    ]
    return {
        "policy_version": "v1.0",
        "description": "Rule-based policy engine separating risk estimation from decision making",
        "tiers": tiers,
        "design_principle": "Models estimate risk; policies make decisions"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
