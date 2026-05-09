import joblib
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple


class CreditPredictor:
    def __init__(self, model_dir: str):
        self.model = joblib.load(os.path.join(model_dir, "lightgbm_credit_model.pkl"))
        self.explainer = joblib.load(os.path.join(model_dir, "shap_explainer.pkl"))
        self.feature_names = joblib.load(os.path.join(model_dir, "feature_names.pkl"))
        self.rgcn_factory = None
        self.rgcn_loaded = False

    def to_dataframe(self, client_data: Dict[str, Any]) -> pd.DataFrame:
        data = {fn: client_data.get(fn, 0) for fn in self.feature_names}
        df = pd.DataFrame([data])
        return df.reindex(columns=self.feature_names, fill_value=0)

    def get_probability(self, df: pd.DataFrame) -> float:
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(df)
            return float(probs[:, 1][0])
        return float(self.model.predict(df)[0])

    def get_shap(self, shap_vals: Any) -> np.ndarray:
        return (
            shap_vals[1]
            if isinstance(shap_vals, list) and len(shap_vals) == 2
            else shap_vals
        )

    def predict(
        self, client_data: Dict[str, Any], use_rgcn: bool = False
    ) -> Dict[str, Any]:
        df = self.to_dataframe(client_data)
        prob = self.get_probability(df)
        rgcn_prob = None

        if use_rgcn and self.rgcn_loaded and self.rgcn_factory:
            try:
                augmented, aug_names = self.rgcn_factory.extract_features(df)
                aug_df = pd.DataFrame(augmented, columns=aug_names)
                rgcn_prob = self.get_probability(aug_df)
                emb = self.rgcn_factory.get_embedding_only(df)
                rgcn_features = {
                    "embeddings": emb[0].tolist(),
                    "similarity_mean": float(augmented[0][-4]),
                    "similarity_max": float(augmented[0][-3]),
                    "similarity_min": float(augmented[0][-2]),
                    "similarity_std": float(augmented[0][-1]),
                }
            except Exception:
                rgcn_features = None
        else:
            rgcn_features = None

        final_prob = rgcn_prob if rgcn_prob is not None else prob
        sv = self.get_shap(self.explainer.shap_values(df))
        vals = sv.flatten()
        idx = np.argsort(np.abs(vals))[::-1][:5]
        risk_factors = [
            {
                "feature": self.feature_names[i],
                "shap_value": float(vals[i]),
                "impact": "increases_risk" if vals[i] > 0 else "decreases_risk",
            }
            for i in idx
        ]

        return {
            "prediction": 1 if final_prob > 0.5 else 0,
            "default_probability": final_prob,
            "base_probability": prob,
            "rgcn_probability": rgcn_prob,
            "rgcn_features": rgcn_features,
            "risk_level": "high"
            if final_prob > 0.5
            else "medium"
            if final_prob > 0.3
            else "low",
            "risk_factors": risk_factors,
            "message": "High risk - declined"
            if final_prob > 0.5
            else "Low risk - approved",
        }

    def load_rgcn(self, model_dir: str):
        # RGCN module temporarily disabled
        self.rgcn_loaded = False
        self.rgcn_factory = None

    def get_model_info(self) -> Dict[str, Any]:
        rgcn_info = None
        if self.rgcn_loaded and self.rgcn_factory:
            rgcn_info = {
                "loaded": True,
                "embedding_dim": getattr(self.rgcn_factory, "embedding_dim", 0),
            }
        return {
            "model_type": "LightGBM + RGCN (optional)",
            "features_count": len(self.feature_names),
            "features": list(self.feature_names),
            "rgcn": rgcn_info,
        }


# Global predictor instance
_predictor = None


def get_predictor() -> CreditPredictor:
    """Get or create the global predictor instance."""
    global _predictor
    if _predictor is None:
        model_dir = os.path.join(os.path.dirname(__file__), "..", "saved_models")
        _predictor = CreditPredictor(model_dir)
        _predictor.load_rgcn(model_dir)
    return _predictor


async def predict_risk_score(request) -> float:
    """
    Predict risk score for a single applicant.

    Args:
        request: PredictionRequest with applicant data

    Returns:
        float: Risk probability (0-1)
    """
    predictor = get_predictor()
    result = predictor.predict(request.dict(), use_rgcn=True)
    return result["default_probability"]


async def batch_predict_risk_scores(applicants: List[Any]) -> List[Dict[str, Any]]:
    """
    Predict risk scores for multiple applicants.

    Args:
        applicants: List of applicant data objects

    Returns:
        List of prediction result dictionaries
    """
    import httpx

    predictor = get_predictor()
    policy_url = os.getenv("POLICY_SERVICE_URL", "http://policy:8000")
    results = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for applicant in applicants:
            result = predictor.predict(applicant.dict(), use_rgcn=True)
            risk_score = result["default_probability"]

            policy_request = {
                "risk_score": risk_score,
                "monthly_income": applicant.monthly_income,
                "debt_ratio": applicant.debt_ratio,
                "employment_months": applicant.employment_months,
                "recent_inquiries": applicant.recent_inquiries,
                "requested_amount": applicant.loan_amount,
            }

            try:
                policy_resp = await client.post(
                    f"{policy_url}/evaluate", json=policy_request
                )
                policy_resp.raise_for_status()
                policy_result = policy_resp.json()
            except Exception:
                policy_result = {
                    "decision": "REVIEW",
                    "risk_grade": "C",
                    "interest_rate": 8.5,
                    "recommended_max_amount": None,
                    "rationale": "Policy service unavailable - manual review required",
                }

            results.append(
                {
                    "applicant_id": applicant.applicant_id,
                    "risk_score": risk_score,
                    "risk_grade": policy_result["risk_grade"],
                    "decision": policy_result["decision"],
                    "interest_rate": policy_result["interest_rate"],
                    "recommended_max_amount": policy_result["recommended_max_amount"],
                    "explanation": policy_result["rationale"],
                }
            )

    return results
    return results
