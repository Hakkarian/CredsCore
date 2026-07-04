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
        # MonthlyIncome training stats: `impute_value` is the floor training
        # used for zeros/NaN (default $1000); the percentiles feed the temporary
        # demo monotonicity correction. See _load_income_stats and
        # _demo_income_correction.
        self.income_stats = self._load_income_stats(model_dir)
        self.income_floor = float(
            self.income_stats.get("impute_value", self.income_stats.get("p01", 1000.0))
        )

    def _load_income_stats(self, model_dir: str) -> Dict[str, Any]:
        """Load MonthlyIncome stats from training_stats.pkl.

        Looks in the model dir root and the active MODEL_VERSION subdir. Falls
        back to default stats if the artifact is missing so imputation and the
        demo fix are always defined.
        """
        candidates = [
            os.path.join(model_dir, "training_stats.pkl"),
            os.path.join(model_dir, os.getenv("MODEL_VERSION", "v2"), "training_stats.pkl"),
        ]
        for path in candidates:
            try:
                stats = joblib.load(path)
            except Exception:
                continue
            income_stats = stats.get("MonthlyIncome", {}) if isinstance(stats, dict) else {}
            if income_stats:
                return income_stats
        return {"impute_value": 1000.0, "p25": 3500.0, "p50": 5437.0, "p75": 8300.0}

    def _demo_income_correction(self, df: pd.DataFrame) -> float:
        """TEMPORARY demo shim — bounded monotonic correction for the inverted
        MonthlyIncome -> risk relationship. REMOVE once the model is retrained
        with monotone_constraints (planned fix #1).

        The trained model learned that LOWER income = LOWER risk (a missing-
        data confound: zero/very-low income rows default less in training).
        Without a retrain we apply a bounded, data-derived correction so risk is
        non-increasing in income: above-median income gets a bounded risk
        reduction, below-median gets a bounded increase.

        Form (approved): correction = -clip(z, -2, 2) * 0.05  (±0.10 max).
        Scale: a ROBUST z-score is used — center = median (p50), scale =
        IQR/1.349 = (p75 - p25)/1.349 — instead of raw mean/std, because the
        raw std (~$14,462) is dominated by the $3M outlier tail and makes the
        correction inert for realistic incomes. Both center and scale come from
        training_stats.pkl, so this stays data-derived (no arbitrary constant).

        Gated by env DEMO_MONOTONIC_FIX=1 so the shim is explicit and trivial
        to disable. Returns 0.0 when disabled or stats are insufficient.
        """
        if os.getenv("DEMO_MONOTONIC_FIX", "0") != "1":
            return 0.0
        p25 = self.income_stats.get("p25")
        p50 = self.income_stats.get("p50")
        p75 = self.income_stats.get("p75")
        if p25 is None or p50 is None or p75 is None:
            return 0.0
        robust_std = (float(p75) - float(p25)) / 1.349
        if robust_std <= 0:
            return 0.0
        if "MonthlyIncome" in df.columns and len(df) > 0:
            income = float(df["MonthlyIncome"].iloc[0])
        else:
            income = self.income_floor
        z = (income - float(p50)) / robust_std
        z = max(-2.0, min(2.0, z))
        return -z * 0.05

    def to_dataframe(self, client_data: Dict[str, Any]) -> pd.DataFrame:
        # Normalize payload keys to match model feature names (hyphen/underscore
        # equivalence). The stored feature_names use hyphens (e.g.
        # "NumberOfTime30-59DaysPastDueNotWorse") while the API contract uses
        # underscores; without normalization those lookups silently default to 0.
        normalized = {
            str(k).replace("-", "_"): v for k, v in client_data.items()
        }
        data = {}
        for feature_name in self.feature_names:
            key = str(feature_name).replace("-", "_")
            if key not in normalized:
                raise KeyError(
                    f"Model feature {feature_name!r} has no value in request payload"
                )
            data[feature_name] = normalized[key]
        df = pd.DataFrame([data])
        df = df.reindex(columns=self.feature_names, fill_value=0)
        # Inference-time imputation: clamp MonthlyIncome below the training
        # floor up to the floor. Mirrors training's zero/NaN -> floor imputation
        # and keeps risk monotonic at the low-income end (no OOD raw zeros).
        if "MonthlyIncome" in df.columns and self.income_floor > 0:
            df["MonthlyIncome"] = df["MonthlyIncome"].apply(
                lambda v: self.income_floor if v < self.income_floor else v
            )
        return df

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
        # TEMPORARY demo shim: enforce income -> risk monotonicity without
        # retraining. See _demo_income_correction. No-op unless
        # DEMO_MONOTONIC_FIX=1. Remove after the #1 monotone_constraints retrain.
        monotonic_correction = self._demo_income_correction(df)
        if monotonic_correction:
            final_prob = max(0.0, min(1.0, final_prob + monotonic_correction))
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
            "monotonic_correction": monotonic_correction,
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
