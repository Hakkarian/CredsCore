import numpy as np
import pandas as pd
import os
import joblib
from typing import Dict, Any
from sklearn.preprocessing import StandardScaler


class SimilarFinder:
    """Find similar applicants with proper feature normalization."""

    def __init__(self, data_path=None):
        if data_path is None:
            # Go up from services/credit_scoring/app/ to CredsCore root, then to data/
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

            # Try multiple possible paths
            possible_paths = [
                os.path.normpath(
                    os.path.join(base_dir, "..", "data", "cs-training.csv")
                ),
                os.path.normpath(
                    os.path.join(base_dir, "..", "..", "data", "cs-training.csv")
                ),
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "..",
                    "data",
                    "cs-training.csv",
                ),
            ]

            # Also check from current working directory
            possible_paths.append(os.path.join(os.getcwd(), "data", "cs-training.csv"))

            # Find the first existing path
            data_path = None
            for p in possible_paths:
                if os.path.exists(p):
                    data_path = p
                    break

            # If still not found, try absolute path from typical project root
            if data_path is None:
                abs_path = "D:\\GitHUB\\CredsCore\\data\\cs-training.csv"
                if os.path.exists(abs_path):
                    data_path = abs_path

        import sys

        print(f"INIT SimilarFinder: data_path={data_path}", file=sys.stderr)
        print(
            f"INIT: path exists={os.path.exists(data_path) if data_path else False}",
            file=sys.stderr,
        )

        self.scaler = None

        if data_path and os.path.exists(data_path):
            self.df = pd.read_csv(data_path)
            print(f"INIT: df columns={self.df.columns[:5].tolist()}", file=sys.stderr)
            # Find the label column - it's named 'SeriousDlqin2yrs'
            label_col = (
                "SeriousDlqin2yrs" if "SeriousDlqin2yrs" in self.df.columns else None
            )
            print(f"INIT: label_col={label_col}", file=sys.stderr)
            self.labels = self.df[label_col].values if label_col else None

            feature_cols = (
                self.df.columns[2:12].tolist()
                if "SeriousDlqin2yrs" in self.df.columns
                else [
                    c
                    for c in self.df.columns
                    if c not in ["Unnamed: 0", "SeriousDlqin2yrs"]
                ][:10]
            )

            # Extract raw features and handle NaN values
            raw_features = self.df[feature_cols].values
            # Fill NaN with median values
            col_medians = np.nanmedian(raw_features, axis=0)
            nan_mask = np.isnan(raw_features)
            raw_features[nan_mask] = np.take(col_medians, np.where(nan_mask)[1])

            # Fit StandardScaler on training features for consistent normalization
            self.scaler = StandardScaler()
            self.features = self.scaler.fit_transform(raw_features).astype('float32')
            self.feature_names = feature_cols
            self.raw_feature_values = raw_features  # Keep raw values for reference

            print(f"INIT: features shape={self.features.shape}", file=sys.stderr)
            print(f"INIT: features normalized with StandardScaler", file=sys.stderr)
            print(
                f"INIT: labels type={type(self.labels)}, len={len(self.labels) if self.labels is not None else None}",
                file=sys.stderr,
            )
        else:
            print(f"Warning: Data file not found at {data_path}", file=sys.stderr)
            self.df = None
            self.features = None
            self.labels = None
            self.feature_names = []
            self.raw_feature_values = None

    def find_similar(self, applicant_data: Dict[str, Any], k: int = 10):
        """Find similar applicants using normalized Euclidean distance."""
        if self.features is None:
            return self._generate_mock_response(applicant_data, k)

        # Map client field names to CSV column names (with dash conversion)
        field_mapping = {
            "RevolvingUtilizationOfUnsecuredLines": "RevolvingUtilizationOfUnsecuredLines",
            "age": "age",
            "NumberOfTime30_59DaysPastDueNotWorse": "NumberOfTime30-59DaysPastDueNotWorse",
            "DebtRatio": "DebtRatio",
            "MonthlyIncome": "MonthlyIncome",
            "NumberOfOpenCreditLinesAndLoans": "NumberOfOpenCreditLinesAndLoans",
            "NumberOfTimes90DaysLate": "NumberOfTimes90DaysLate",
            "NumberRealEstateLoansOrLines": "NumberRealEstateLoansOrLines",
            "NumberOfTime60_89DaysPastDueNotWorse": "NumberOfTime60-89DaysPastDueNotWorse",
            "NumberOfDependents": "NumberOfDependents",
        }

        # Build applicant feature vector from input
        applicant_raw_features = []
        for i, col in enumerate(self.feature_names):
            client_field = next((k for k, v in field_mapping.items() if v == col), None)
            val = applicant_data.get(client_field, 0) if client_field else 0
            # Handle NaN
            if pd.isna(val):
                val = 0
            applicant_raw_features.append(val)

        applicant_raw = np.array(applicant_raw_features).reshape(1, -1)

        # Normalize using the same scaler fit on training data
        if self.scaler is not None:
            applicant_features = self.scaler.transform(applicant_raw).flatten()
        else:
            applicant_features = applicant_raw.flatten()

        # Calculate Euclidean distances in normalized space
        distances = np.linalg.norm(self.features - applicant_features, axis=1)
        k = min(k, len(distances))
        nearest_indices = np.argsort(distances)[:k]
        nearest_distances = distances[nearest_indices]

        if self.labels is not None:
            nearest_labels = self.labels[nearest_indices]
            try:
                default_count = int(np.sum(nearest_labels))
            except:
                default_count = int(sum(nearest_labels.tolist()))
        else:
            default_count = k // 2

        default_rate = default_count / k

        # Calculate average distance (similarity) for context
        avg_distance = float(np.mean(nearest_distances)) if len(nearest_distances) > 0 else 1.0
        max_distance = float(np.max(nearest_distances)) if len(nearest_distances) > 0 else 1.0

        # Normalize distances to 0-1 scale (invert so closer = higher similarity)
        similarity_score = max(0, 1 - avg_distance)

        # Risk assessment based on BOTH default rate AND model-like thresholds
        # Align with predictor thresholds: >0.5 high, 0.3-0.5 medium, <0.3 low
        if default_rate > 0.5:
            risk_level = "high"
        elif default_rate > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"

        # If neighbors are very far (low similarity), reduce confidence in the risk assessment
        # Avg distance in normalized space ~2-5 is typical, >5 is far
        neighbor_confidence = max(0, 1 - (avg_distance / 5))
        if neighbor_confidence < 0.3:
            # When neighbors are too far, flag as uncertain but keep the risk level
            risk_level = "uncertain" if default_rate < 0.3 else risk_level

        # Map default rate to estimated probability with neighbor distance adjustment
        # Closer neighbors = more confident = closer to historical rate
        # Farther neighbors = less confident = regressed toward population mean
        population_default_rate = 0.0668  # ~6.68% from training data

        # Adjust probability based on similarity
        if neighbor_confidence > 0.8:
            estimated_probability = default_rate
        elif neighbor_confidence > 0.5:
            estimated_probability = default_rate * 0.7 + population_default_rate * 0.3
        else:
            estimated_probability = default_rate * 0.4 + population_default_rate * 0.6

        return {
            "applicant": applicant_data,
            "estimated_probability": round(estimated_probability, 3),
            "neighbor_confidence": round(neighbor_confidence, 3),
            "avg_distance": round(avg_distance, 3),
            "similar_applicants": {
                "similar_indices": nearest_indices.tolist(),
                "distances": nearest_distances.tolist(),
                "default_labels": nearest_labels.tolist()
                if self.labels is not None
                else [],
                "default_count": default_count,
                "total_similar": k,
                "default_rate": round(default_rate, 3),
                "risk_assessment": risk_level,
            },
            "interpretation": {
                "default_rate": f"Among {k} similar applicants, {default_count} ({default_rate * 100:.1f}%) defaulted.",
                "risk_assessment": f"Based on similar applicant outcomes, this applicant has {risk_level} risk.",
                "summary": f"Found {k} similar applicants with {default_rate * 100:.1f}% default rate.",
            },
            "human_explanation": (
            f"Analysis of {k} similar past applicants reveals a {default_rate * 100:.1f}% historical default rate. "
            f"The nearest neighbors are on average {avg_distance:.2f} units away (confidence: {neighbor_confidence:.0%}). "
            f"Based on the similarity-adjusted estimate, this applicant has a {estimated_probability:.1%} predicted probability of default "
            f"({risk_level} risk level)."
        ),
        }


_similar_finder = None


def get_similar_finder():
    global _similar_finder
    if _similar_finder is None:
        _similar_finder = SimilarFinder()
    return _similar_finder


def find_similar_applicants(applicant_data: Dict[str, Any], k: int = 10):
    finder = get_similar_finder()
    return finder.find_similar(applicant_data, k)
