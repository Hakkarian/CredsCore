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
        return shap_vals[1] if isinstance(shap_vals, list) and len(shap_vals) == 2 else shap_vals

    def predict(self, client_data: Dict[str, Any], use_rgcn: bool = False) -> Dict[str, Any]:
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
            "risk_level": "high" if final_prob > 0.5 else "medium" if final_prob > 0.3 else "low",
            "risk_factors": risk_factors,
            "message": "High risk - declined" if final_prob > 0.5 else "Low risk - approved",
        }

    def load_rgcn(self, model_dir: str):
        rgcn_path = os.path.join(model_dir, "rgcn_meta.pkl")
        rgcn_model_path = os.path.join(model_dir, "rgcn_model.pt")
        if os.path.exists(rgcn_path) and os.path.exists(rgcn_model_path):
            try:
                from app.rgcn import RGCNFeatureFactory
                self.rgcn_factory = RGCNFeatureFactory()
                self.rgcn_factory.load(model_dir)
                self.rgcn_loaded = True
            except Exception as e:
                print(f"Warning: Could not load RGCN: {e}")

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