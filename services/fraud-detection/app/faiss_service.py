import faiss
import numpy as np
import joblib
import os
from typing import Dict, Any, List, Optional


class FAISSService:
    def __init__(self, model_dir: str):
        self.index = None
        self.training_data = None
        self.feature_names = None
        self.load(model_dir)

    def load(self, model_dir: str):
        index_path = os.path.join(model_dir, "faiss_index.index")
        meta_path = os.path.join(model_dir, "faiss_meta.pkl")
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        if os.path.exists(meta_path):
            meta = joblib.load(meta_path)
            self.training_data = meta.get("training_data")
            self.feature_names = meta.get("feature_names", [])

    def find_similar(self, features: np.ndarray, k: int = 10) -> Dict[str, Any]:
        if not self.index or self.training_data is None:
            return {"error": "FAISS index not loaded"}
        features = features.reshape(1, -1).astype("float32")
        faiss.normalize_L2(features)
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(features, k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            results.append({
                "index": int(idx),
                "distance": float(distances[0][i]),
            })
        return {"similar_applicants": results, "total": len(results)}

    def get_neighbor_risk(self, features: np.ndarray, k: int = 20) -> Dict[str, Any]:
        similar = self.find_similar(features, k)
        if "error" in similar:
            return similar
        total_risk = 0
        default_count = 0
        for app in similar["similar_applicants"]:
            idx = app["index"]
            if self.training_data is not None and idx < len(self.training_data):
                total_risk += 1
        avg_distance = np.mean([a["distance"] for a in similar["similar_applicants"]]) if similar["similar_applicants"] else 0
        return {
            "neighbor_count": len(similar["similar_applicants"]),
            "avg_distance": float(avg_distance),
        }