"""FAISS service with fixed probability calculation using distance as risk signal."""

import faiss
import numpy as np
import pickle
import os
from typing import Dict, Any, List, Optional


class FAISSService:
    """FAISS service for similarity search with distance-as-risk calculation."""

    def __init__(self, model_dir: str):
        self.index = None
        self.scaler = None
        self.training_data = None
        self.feature_names = None
        self.labels = None
        self.model_dir = model_dir
        self.loaded = False
        self.mean_distance = None  # Store mean training distance for normalization
        self.std_distance = None  # Store std for normalization
        self.load(model_dir)

    def load(self, model_dir: str):
        """Load FAISS index with scaler and metadata."""
        index_path = os.path.join(model_dir, "faiss_index.index")
        meta_path = os.path.join(model_dir, "faiss_meta.pkl")

        if os.path.exists(index_path) and os.path.exists(meta_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(meta_path, 'rb') as f:
                    meta = pickle.load(f)
                self.scaler = meta.get("scaler")
                self.feature_names = meta.get("feature_names", [])
                self.labels = meta.get("labels")
                self.training_data = meta.get("training_data")
                self.loaded = True
                print(f"Loaded FAISS index: {self.index.ntotal} vectors, {len(self.feature_names)} features")

                # Calculate training distance statistics for risk scaling
                self._calculate_distance_statistics()
            except Exception as e:
                print(f"Warning: Could not load FAISS index: {e}")
                self._create_dummy_index()
        else:
            print(f"FAISS files not found in {model_dir}, creating dummy index")
            self._create_dummy_index()

    def _calculate_distance_statistics(self):
        """Calculate mean/std of inter-point distances for risk normalization."""
        if self.training_data is None or self.index is None:
            return

        # Sample distances from training data to get distribution
        sample_size = min(1000, self.index.ntotal)
        indices = np.random.choice(self.index.ntotal, sample_size, replace=False)

        # Get vectors and calculate self-distances
        distances_list = []
        for idx in indices[:100]:  # Sample 100 points for efficiency
            vec = self.training_data[idx:idx+1].astype("float32")
            _, dists = self.index.search(vec, 10)
            distances_list.append(np.mean(dists[0][1:]))  # Exclude self (distance 0)

        if distances_list:
            self.mean_distance = np.mean(distances_list)
            self.std_distance = np.std(distances_list) + 1e-6  # Avoid div by zero
        else:
            self.mean_distance = 1.0
            self.std_distance = 1.0

    def _create_dummy_index(self):
        """Create a dummy index for testing when real index not available."""
        from sklearn.preprocessing import StandardScaler
        dim = 10

        # Create quantizer and IVF index
        quantizer = faiss.IndexFlatL2(dim)
        self.index = faiss.IndexIVFFlat(quantizer, dim, 10)

        # Generate dummy training data
        dummy_data = np.random.rand(100, dim).astype("float32")
        self.scaler = StandardScaler()
        dummy_scaled = self.scaler.fit_transform(dummy_data).astype("float32")

        # Train and add
        self.index.train(dummy_scaled)
        self.index.add(dummy_scaled)

        self.labels = np.array([0] * 50 + [1] * 50)
        self.training_data = dummy_scaled
        self.feature_names = [
            "RevolvingUtilizationOfUnsecuredLines",
            "age",
            "NumberOfTime30-59DaysPastDueNotWorse",
            "DebtRatio",
            "MonthlyIncome",
            "NumberOfOpenCreditLinesAndLoans",
            "NumberOfTimes90DaysLate",
            "NumberRealEstateLoansOrLines",
            "NumberOfTime60-89DaysPastDueNotWorse",
            "NumberOfDependents",
        ]
        self.mean_distance = 1.0
        self.std_distance = 0.5
        print("Created dummy FAISS index for testing")

    def _calculate_distance_risk_factor(self, avg_distance: float) -> float:
        """
        Calculate risk factor based on distance from training distribution.
        High distance = anomalous = potential risk factor.
        """
        if self.mean_distance is None or self.mean_distance == 0:
            return 0.0

        # Normalize distance by training distribution
        normalized_distance = (avg_distance - self.mean_distance) / self.std_distance

        # Convert to risk factor: sigmoid-like curve
        # Distance 0-1 std above mean: low additional risk
        # Distance >2 std above mean: significant additional risk
        risk_factor = 1 / (1 + np.exp(-(normalized_distance - 1)))

        return float(risk_factor)

    def find_similar(self, features: np.ndarray, k: int = 10) -> Dict[str, Any]:
        """Find similar applicants using FAISS with distance-as-risk calculation."""
        if not self.index:
            return {"error": "FAISS index not loaded"}

        # Ensure features is the right shape
        features = features.reshape(1, -1).astype("float32")

        # Apply the same scaling as during training
        if self.scaler is not None:
            features = self.scaler.transform(features).astype("float32")

        k = min(k, self.index.ntotal)

        # Set nprobe for IVF indexes (does nothing for Flat indexes)
        if hasattr(self.index, 'nprobe'):
            self.index.nprobe = 10

        distances, indices = self.index.search(features, k)

        results = []
        default_count = 0
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue

            # Get default label if available
            is_default = False
            if self.labels is not None and idx < len(self.labels):
                is_default = bool(self.labels[idx])
            if is_default:
                default_count += 1

            results.append({
                "index": int(idx),
                "distance": float(distances[0][i]),
                "default": is_default,
            })

        # Calculate default rate and estimated probability
        total = len(results)
        default_rate = default_count / total if total > 0 else 0.5

        # Calculate average distance
        avg_distance = float(sum(r["distance"] for r in results) / len(results)) if results else 1.0

        # Calculate distance-based risk factor
        # Anomalous inputs (high distance) are themselves a risk signal
        distance_risk = self._calculate_distance_risk_factor(avg_distance)

        # Calculate neighbor confidence (information quality, for reference only)
        # Cap distance contribution to confidence at reasonable levels
        confidence_distance = min(avg_distance, 10.0)
        neighbor_confidence = max(0, 1 - (confidence_distance / 5))

        # NEW: Use distance as a PRIMARY risk signal, not a penalty
        # When neighbors are close -> trust default_rate
        # When neighbors are distant/extreme outlier -> distance ITSELF is the signal
        population_default_rate = 0.0668  # ~6.68% from training data

        # Calculate outlier severity
        if self.mean_distance and self.std_distance:
            outlier_score = (avg_distance - self.mean_distance) / self.std_distance
        else:
            outlier_score = avg_distance / 10.0

        # Distance thresholds based on training distribution
        EXTREME_OUTLIER_THRESHOLD = 5.0  # 5 std deviations from mean
        HIGH_OUTLIER_THRESHOLD = 2.0     # 2 std deviations from mean

        if neighbor_confidence > 0.8:
            # Close neighbors - trust the local default rate
            estimated_probability = default_rate
        elif neighbor_confidence > 0.5:
            # Moderate distance - blend default rate with some distance risk
            estimated_probability = default_rate * 0.8 + distance_risk * 0.2
        elif outlier_score > EXTREME_OUTLIER_THRESHOLD:
            # EXTREME OUTLIER: The lack of similar training cases IS the risk
            # Extremely high distance = no close matches = unknown/untested territory = high risk
            # Use distance_risk as primary signal, with default_rate as floor
            estimated_probability = max(
                0.6,  # Minimum high risk for extreme outliers
                distance_risk * 0.8 + default_rate * 0.2
            )
        elif outlier_score > HIGH_OUTLIER_THRESHOLD:
            # HIGH OUTLIER: Blend distance and default rate, but favor default_rate
            # Being an outlier adds risk, but default_rate from far neighbors still matters
            estimated_probability = max(
                default_rate,  # Never below what neighbors show
                default_rate * 0.6 + distance_risk * 0.4
            )
        else:
            # Moderate outlier - standard blend
            estimated_probability = max(
                default_rate * 0.7 + population_default_rate * 0.3,
                default_rate * 0.5 + distance_risk * 0.3
            )

        # Ensure probability is bounded
        estimated_probability = min(1.0, max(0.0, estimated_probability))

        # Determine risk level based on estimated probability
        # More granular thresholds
        if estimated_probability > 0.6:
            risk_level = "high"
        elif estimated_probability > 0.3:
            risk_level = "medium"
        elif estimated_probability > 0.1:
            risk_level = "low-medium"
        else:
            risk_level = "low"

        return {
            "similar_applicants": results,
            "total": total,
            "default_count": default_count,
            "default_rate": round(default_rate, 3),
            "estimated_probability": round(estimated_probability, 3),
            "neighbor_confidence": round(neighbor_confidence, 3),
            "distance_risk_factor": round(distance_risk, 3),
            "avg_distance": round(avg_distance, 3),
            "risk_assessment": risk_level,
        }

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
        avg_distance = (
            np.mean([a["distance"] for a in similar["similar_applicants"]])
            if similar["similar_applicants"]
            else 0
        )
        return {
            "neighbor_count": len(similar["similar_applicants"]),
            "avg_distance": float(avg_distance),
        }
