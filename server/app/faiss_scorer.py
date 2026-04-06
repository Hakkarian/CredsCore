import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from sklearn.metrics.pairwise import cosine_similarity


class FAISSRealTimeScorer:
    """Evaluates individual applicants using FAISS similarity search for real-time risk scoring."""

    def __init__(self, faiss_index):
        self.faiss_index = faiss_index
        self.fraud_threshold = 0.7
        self.anomaly_threshold = 2.0

    def score_applicant(self, applicant_data: pd.DataFrame, k: int = 20) -> Dict[str, Any]:
        """Compute enhanced risk score for an individual applicant using FAISS neighbor analysis."""
        if not self.faiss_index.index_trained:
            raise ValueError("FAISS index not trained. Call build_index first.")

        neighbor_info = self.faiss_index.get_neighbor_features(applicant_data, k=k)

        distances, indices = self.faiss_index.search_similar(applicant_data.values, k=k)
        labels = self.faiss_index.labels[indices[0]]
        dists = distances[0]

        weighted_risk = self._compute_weighted_risk(labels, dists)
        default_neighbor_ratio = labels.sum() / len(labels)
        anomaly_score = self._compute_anomaly_score(applicant_data, indices[0], dists)
        fraud_indicator = self._detect_fraud_signals(applicant_data, labels, dists, k)

        base_score = self._estimate_risk_from_neighbors(weighted_risk, default_neighbor_ratio)
        enhanced_score = self._adjust_for_fraud_signals(base_score, fraud_indicator)

        return {
            "enhanced_risk_score": float(enhanced_score),
            "base_neighbor_risk": float(base_score),
            "weighted_neighbor_risk": float(weighted_risk),
            "default_neighbor_ratio": float(default_neighbor_ratio),
            "anomaly_score": float(anomaly_score),
            "fraud_indicator": fraud_indicator,
            "risk_level": self._classify_risk(enhanced_score),
            "neighbor_stats": {
                "avg_distance": float(dists.mean()),
                "min_distance": float(dists.min()),
                "max_distance": float(dists.max()),
                "std_distance": float(dists.std()),
            },
        }

    def get_fraud_indicators(self, applicant_data: pd.DataFrame, k: int = 20) -> Dict[str, Any]:
        """Detect if applicant shows signals of being connected to fraud patterns."""
        distances, indices = self.faiss_index.search_similar(applicant_data.values, k=k)
        labels = self.faiss_index.labels[indices[0]]
        dists = distances[0]

        high_risk_neighbors = int((labels == 1).sum())
        high_risk_ratio = high_risk_neighbors / k

        close_to_fraud = self._count_close_high_risk_neighbors(applicant_data, labels, dists, threshold=0.5)

        anomaly_score = self._compute_anomaly_score(applicant_data, indices[0], dists)

        is_suspicious = (
            high_risk_ratio > self.fraud_threshold
            or close_to_fraud >= 3
            or anomaly_score > self.anomaly_threshold
        )

        return {
            "is_suspicious": bool(is_suspicious),
            "high_risk_neighbor_ratio": float(high_risk_ratio),
            "close_high_risk_neighbors": int(close_to_fraud),
            "anomaly_score": float(anomaly_score),
            "suspicion_level": "high" if high_risk_ratio > 0.8 else "medium" if high_risk_ratio > 0.5 else "low",
            "risk_factors": self._list_risk_factors(applicant_data, labels, dists, anomaly_score),
        }

    def compute_neighbor_anomaly(self, applicant_data: pd.DataFrame, k: int = 10) -> Dict[str, Any]:
        """Measure how anomalous an applicant is compared to their nearest neighbors."""
        distances, indices = self.faiss_index.search_similar(applicant_data.values, k=k)
        dists = distances[0]

        training_features = self.faiss_index.training_data[indices[0]]
        query = self.faiss_index.scaler.transform(applicant_data.values).astype("float32")

        neighbor_mean = training_features.mean(axis=0)
        neighbor_std = training_features.std(axis=0) + 1e-8
        z_scores = np.abs((query[0] - neighbor_mean) / neighbor_std)

        top_deviant_features = np.argsort(z_scores)[::-1][:5]
        feature_names = self.faiss_index.feature_names or []

        deviant_features = [
            {
                "feature": feature_names[i] if i < len(feature_names) else f"feature_{i}",
                "z_score": float(z_scores[i]),
                "applicant_value": float(query[0][i]),
                "neighbor_mean": float(neighbor_mean[i]),
                "neighbor_std": float(neighbor_std[i]),
            }
            for i in top_deviant_features
        ]

        overall_anomaly = float(np.mean(z_scores))

        return {
            "overall_anomaly_score": overall_anomaly,
            "avg_neighbor_distance": float(dists.mean()),
            "distance_std": float(dists.std()),
            "deviant_features": deviant_features,
            "is_outlier": overall_anomaly > self.anomaly_threshold,
        }

    def _compute_weighted_risk(self, labels: np.ndarray, distances: np.ndarray) -> float:
        weights = 1.0 / (distances + 1e-6)
        weights = weights / weights.sum()
        return float(np.dot(labels.astype(float), weights))

    def _compute_anomaly_score(self, applicant_data: pd.DataFrame, neighbor_indices: np.ndarray, distances: np.ndarray) -> float:
        training_features = self.faiss_index.training_data[neighbor_indices]
        query = self.faiss_index.scaler.transform(applicant_data.values).astype("float32")

        centroid = training_features.mean(axis=0)
        dist_to_centroid = float(np.linalg.norm(query[0] - centroid))

        neighbor_dists_to_centroid = np.linalg.norm(training_features - centroid, axis=1)
        mean_neighbor_dist = neighbor_dists_to_centroid.mean()
        std_neighbor_dist = neighbor_dists_to_centroid.std() + 1e-8

        return (dist_to_centroid - mean_neighbor_dist) / std_neighbor_dist

    def _detect_fraud_signals(self, applicant_data: pd.DataFrame, labels: np.ndarray, distances: np.ndarray, k: int) -> Dict[str, Any]:
        high_risk_mask = labels == 1
        high_risk_dists = distances[high_risk_mask]
        low_risk_dists = distances[~high_risk_mask]

        signal = {
            "high_risk_cluster_proximity": float(high_risk_dists.min()) if len(high_risk_dists) > 0 else float("inf"),
            "risk_concentration": float(high_risk_mask.sum()) / k,
        }

        if len(high_risk_dists) >= 3 and len(low_risk_dists) > 0:
            signal["avg_high_risk_distance"] = float(high_risk_dists.mean())
            signal["avg_low_risk_distance"] = float(low_risk_dists.mean())
            signal["distance_ratio"] = float(high_risk_dists.mean() / (low_risk_dists.mean() + 1e-8))

        return signal

    def _estimate_risk_from_neighbors(self, weighted_risk: float, default_ratio: float) -> float:
        alpha = 0.6
        return alpha * weighted_risk + (1 - alpha) * default_ratio

    def _adjust_for_fraud_signals(self, base_score: float, fraud_indicator: Dict[str, Any]) -> float:
        concentration = fraud_indicator.get("risk_concentration", 0)
        adjustment = min(0.15, concentration * 0.2)
        return min(1.0, base_score + adjustment)

    def _classify_risk(self, score: float) -> str:
        if score > 0.6:
            return "high"
        elif score > 0.35:
            return "medium"
        return "low"

    def _count_close_high_risk_neighbors(self, applicant_data: pd.DataFrame, labels: np.ndarray, distances: np.ndarray, threshold: float) -> int:
        high_risk_mask = labels == 1
        close_mask = distances < threshold
        return int((high_risk_mask & close_mask).sum())

    def _list_risk_factors(self, applicant_data: pd.DataFrame, labels: np.ndarray, distances: np.ndarray, anomaly_score: float) -> List[str]:
        factors = []
        high_risk_ratio = (labels == 1).sum() / len(labels)
        if high_risk_ratio > 0.5:
            factors.append(f"High proportion of similar historical applicants defaulted ({high_risk_ratio:.0%})")
        if distances.min() < 0.5 and (labels == 1).sum() > 0:
            factors.append("Very close match to known defaulter(s)")
        if anomaly_score > self.anomaly_threshold:
            factors.append(f"Applicant profile is anomalous compared to neighbors (score: {anomaly_score:.1f})")
        return factors if factors else ["No significant fraud signals detected"]