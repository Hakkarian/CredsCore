import numpy as np
import pandas as pd
import os
from typing import List, Dict, Any


# Feature names (underscore version - matches API)
FEATURE_NAMES = [
    "RevolvingUtilizationOfUnsecuredLines",
    "age",
    "NumberOfTime30_59DaysPastDueNotWorse",
    "DebtRatio",
    "MonthlyIncome",
    "NumberOfOpenCreditLinesAndLoans",
    "NumberOfTimes90DaysLate",
    "NumberRealEstateLoansOrLines",
    "NumberOfTime60_89DaysPastDueNotWorse",
    "NumberOfDependents",
]

# CSV column names (dash version - matches cs-training.csv)
CSV_COLUMNS = [
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

# Training statistics computed from cs-training.csv
def _load_training_stats():
    """Load actual training statistics from CSV if available."""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "cs-training.csv"),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "cs-training.csv"),
        "/d/GitHUB/CredsCore/data/cs-training.csv",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                if 'Unnamed: 0' in df.columns:
                    df = df.drop('Unnamed: 0', axis=1)

                # Select only the feature columns (using CSV column names)
                feature_cols = [c for c in df.columns if c in CSV_COLUMNS]
                if len(feature_cols) == len(CSV_COLUMNS):
                    stats_df = df[feature_cols]
                    mean = stats_df.mean().values
                    std = stats_df.std().values
                    # Replace zero std with 1 to avoid division by zero
                    std = np.where(std == 0, 1, std)
                    return mean, std, df['SeriousDlqin2yrs'].mean() if 'SeriousDlqin2yrs' in df.columns else 0.0668
            except Exception as e:
                print(f"Warning: Could not load training stats from {path}: {e}")
                continue

    # Fallback to hardcoded values
    return (
        np.array([0.249900, 41.915012, 0.265314, 0.358154, 5806.383669,
                  4.980091, 0.265863, 1.022385, 0.183253, 1.492200]),
        np.array([0.352835, 17.969860, 0.578535, 0.499737, 6980.651993,
                  2.405678, 0.564855, 1.559558, 0.488754, 1.304361]),
        0.0668
    )

TRAIN_MEAN, TRAIN_STD, TRAIN_DEFAULT_RATE = _load_training_stats()


def _to_feature_vector(data: Dict[str, Any]) -> List[float]:
    """Extract features in consistent order, handling dash/underscore variations."""
    # Map feature names to handle both dash and underscore versions
    def get_val(key: str) -> float:
        # Try underscore version first
        if key in data:
            return float(data.get(key, 0) or 0)
        # Try dash version
        dash_key = key.replace("_", "-")
        if dash_key in data:
            return float(data.get(dash_key, 0) or 0)
        # Try common variations
        return 0.0

    return [
        get_val("RevolvingUtilizationOfUnsecuredLines"),
        get_val("age"),
        get_val("NumberOfTime30_59DaysPastDueNotWorse"),  # Maps to NumberOfTime30-59DaysPastDueNotWorse
        get_val("DebtRatio"),
        get_val("MonthlyIncome"),
        get_val("NumberOfOpenCreditLinesAndLoans"),
        get_val("NumberOfTimes90DaysLate"),
        get_val("NumberRealEstateLoansOrLines"),
        get_val("NumberOfTime60_89DaysPastDueNotWorse"),  # Maps to NumberOfTime60-89DaysPastDueNotWorse
        get_val("NumberOfDependents"),
    ]


def _compute_wasserstein_distance(new_data: np.ndarray, train_mean: np.ndarray, train_std: np.ndarray) -> float:
    """Compute normalized Wasserstein distance between distributions."""
    # Normalize new data using training statistics
    new_normalized = (new_data - train_mean) / (train_std + 1e-8)
    # Compare means of normalized distributions
    return float(np.mean(np.abs(new_normalized.mean(axis=0))))


class DriftAnalyzer:
    """Analyzes model drift using multiple statistical measures."""

    def __init__(self):
        self.train_mean = TRAIN_MEAN
        self.train_std = TRAIN_STD
        self.train_default_rate = TRAIN_DEFAULT_RATE

    def compute_cluster_based_drift(self, new_data: np.ndarray, n_clusters: int = 10) -> Dict[str, Any]:
        """Compute drift using KMeans cluster centroids."""
        try:
            from sklearn.cluster import KMeans

            n_clusters = min(n_clusters, len(new_data))

            # Normalize new data with training statistics
            new_normalized = (new_data - self.train_mean[:new_data.shape[1]]) / (self.train_std[:new_data.shape[1]] + 1e-8)

            # Fit KMeans on new data
            kmeans_new = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            kmeans_new.fit(new_normalized)
            new_centroids = kmeans_new.cluster_centers_

            # Generate synthetic training centroids from training distribution
            np.random.seed(42)
            train_samples = np.random.randn(min(1000, len(new_data) * 2), new_data.shape[1])
            train_samples = train_samples * self.train_std[:new_data.shape[1]] + self.train_mean[:new_data.shape[1]]
            train_normalized = (train_samples - self.train_mean[:new_data.shape[1]]) / (self.train_std[:new_data.shape[1]] + 1e-8)

            kmeans_train = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            kmeans_train.fit(train_normalized)
            train_centroids = kmeans_train.cluster_centers_

            # Compute distances between centroids (using numpy instead of scipy)
            distances = []
            for train_c in train_centroids:
                for new_c in new_centroids:
                    dist = np.linalg.norm(train_c - new_c)
                    distances.append(dist)

            distances = np.array(distances).reshape(len(train_centroids), len(new_centroids))
            min_dists = distances.min(axis=1)

            return {
                "avg_centroid_distance": float(np.mean(min_dists)),
                "max_centroid_distance": float(np.max(min_dists)),
                "std_centroid_distance": float(np.std(min_dists)),
            }
        except Exception as e:
            # Fallback to simple mean comparison
            return self._simple_drift(new_data)

    def _simple_drift(self, new_data: np.ndarray) -> Dict[str, Any]:
        """Simple drift: compare normalized means with proper dimension handling."""
        new_mean = new_data.mean(axis=0)
        n_features = new_data.shape[1]
        # Ensure we only use available dimensions
        train_mean = self.train_mean[:n_features] if len(self.train_mean) >= n_features else self.train_mean
        train_std = self.train_std[:n_features] if len(self.train_std) >= n_features else self.train_std

        # Pad if needed
        if len(train_mean) < n_features:
            train_mean = np.pad(train_mean, (0, n_features - len(train_mean)), mode='edge')
        if len(train_std) < n_features:
            train_std = np.pad(train_std, (0, n_features - len(train_std)), mode='ones')

        norm_diffs = np.abs(new_mean - train_mean) / (train_std + 1e-8)

        return {
            "avg_centroid_distance": float(np.mean(norm_diffs)),
            "max_centroid_distance": float(np.max(norm_diffs)),
            "std_centroid_distance": float(np.std(norm_diffs)),
        }

    def compute_kl_divergence(self, new_data: np.ndarray, n_features: int = None) -> float:
        """Compute KL divergence between feature distributions."""
        n_features = n_features or new_data.shape[1]
        n_features = min(n_features, new_data.shape[1], len(self.train_mean))
        kl_divs = []
        for i in range(n_features):
            new_vals = new_data[:, i]
            train_mean = self.train_mean[i]
            train_std = self.train_std[i]

            # Simple binning-based KL
            bins = np.linspace(
                min(new_vals.min(), train_mean - 3 * train_std),
                max(new_vals.max(), train_mean + 3 * train_std),
                20
            )

            new_hist, _ = np.histogram(new_vals, bins=bins, density=True)
            # Generate synthetic training distribution
            train_vals = np.random.normal(train_mean, train_std, len(new_vals))
            train_hist, _ = np.histogram(train_vals, bins=bins, density=True)

            # Add epsilon to avoid log(0)
            new_hist = new_hist + 1e-10
            train_hist = train_hist + 1e-10
            new_hist = new_hist / new_hist.sum()
            train_hist = train_hist / train_hist.sum()

            kl = np.sum(new_hist * np.log(new_hist / train_hist))
            kl_divs.append(abs(kl))

        return float(np.mean(kl_divs))

    def compute_population_zscore(self, new_data: np.ndarray, n_features: int = None) -> float:
        """Population stability index via z-scores."""
        n_features = n_features or new_data.shape[1]
        z_scores = []
        for i in range(min(new_data.shape[1], len(self.train_mean), n_features)):
            mean_diff = new_data[:, i].mean() - self.train_mean[i]
            std_combined = np.sqrt(
                (self.train_std[i] ** 2 + new_data[:, i].std() ** 2) / 2
            )
            z_scores.append(abs(mean_diff) / (std_combined + 1e-8))
        return float(np.mean(z_scores)) if z_scores else 0.0


# DEPRECATED: Old simple implementation kept for reference
def old_monitor_model_drift(new_data: List[Dict[str, Any]], n_clusters: int = 10):
    pass


def monitor_model_drift(new_data: List[Dict[str, Any]], n_clusters: int = 10):
    """Monitor model drift using actual training statistics and multiple statistical measures."""
    try:
        if not new_data:
            return _empty_drift_result()

        # Convert to feature matrix with consistent feature ordering
        data_matrix = np.array([_to_feature_vector(record) for record in new_data])

        # Remove any NaN values
        data_matrix = np.nan_to_num(data_matrix, nan=0.0, posinf=0.0, neginf=0.0)

        if data_matrix.shape[0] == 0:
            return _empty_drift_result()

        analyzer = DriftAnalyzer()
        n_features = min(data_matrix.shape[1], len(analyzer.train_mean))

        # Ensure we use matching dimensions
        train_mean = analyzer.train_mean[:n_features]
        train_std = analyzer.train_std[:n_features]
        data_matrix = data_matrix[:, :n_features]

        # 1. Compute standardized drift metrics
        z_drift = analyzer.compute_population_zscore(data_matrix, n_features)

        # 2. Compute KL divergence per feature
        kl_div = analyzer.compute_kl_divergence(data_matrix, n_features)

        # 3. Compute centroid-based drift
        n_clusters = min(n_clusters, len(new_data))
        centroid_metrics = analyzer.compute_cluster_based_drift(data_matrix, n_clusters)

        # 4. Compute Wasserstein distance (mean normalized shift)
        wasserstein = z_drift  # Use z-score as proxy for normalized distribution distance

        # Combined drift score (weighted average of normalized metrics)
        # Normalize each metric to 0-1 scale using typical thresholds
        kl_normalized = min(kl_div / 0.5, 1.0)  # KL > 0.5 is high
        z_normalized = min(z_drift / 2.0, 1.0)  # Z > 2.0 is significant
        centroid_normalized = min(centroid_metrics["avg_centroid_distance"] / 2.0, 1.0)

        combined_drift_score = (
            kl_normalized * 0.35 +      # KL divergence: 35%
            z_normalized * 0.35 +       # Z-score drift: 35%
            centroid_normalized * 0.30  # Centroid drift: 30%
        )

        # Thresholds for drift levels (using combined score)
        drift_detected = bool(combined_drift_score > 0.15)  # 15% combined drift
        drift_level = "high" if combined_drift_score > 0.40 else "medium" if combined_drift_score > 0.15 else "low"

        # Feature-level drift analysis
        feature_drifts = []
        for i, name in enumerate(FEATURE_NAMES[:n_features]):
            new_mean = data_matrix[:, i].mean()
            train_mean_i = train_mean[i]
            train_std_i = train_std[i]
            z_score = abs(new_mean - train_mean_i) / (train_std_i + 1e-8)
            feature_drifts.append({
                "feature": name,
                "z_score": round(float(z_score), 3),
                "drift_detected": bool(z_score > 2.0),
                "new_mean": round(float(new_mean), 4),
                "train_mean": round(float(train_mean_i), 4),
            })

        # Sort by most drifted features
        feature_drifts.sort(key=lambda x: x["z_score"], reverse=True)

        return {
            "drift_analysis": {
                "combined_drift_score": round(combined_drift_score, 4),
                "avg_centroid_distance": round(centroid_metrics["avg_centroid_distance"], 4),
                "max_centroid_distance": round(centroid_metrics["max_centroid_distance"], 4),
                "kl_divergence": round(kl_div, 4),
                "z_score_drift": round(z_drift, 4),
                "wasserstein_distance": round(wasserstein, 4),
                "drift_detected": drift_detected,
                "drift_level": drift_level,
                "sample_size": len(new_data),
                "feature_drifts": feature_drifts[:5],  # Top 5 drifted features
                "train_distribution": train_mean.tolist(),
                "new_distribution": data_matrix.mean(axis=0).tolist(),
            },
            "interpretation": {
                "drift_detected": str(drift_detected).lower(),
                "drift_level": drift_level,
                "kl_divergence": f"{kl_div:.4f}",
                "avg_centroid_shift": f"{centroid_metrics['avg_centroid_distance']:.4f}",
                "z_score_drift": f"{z_drift:.4f}",
                "recommendation": _get_drift_recommendation(drift_level, feature_drifts),
            },
            "human_explanation": _format_drift_explanation(len(new_data), drift_level, combined_drift_score,
                                                          feature_drifts, centroid_metrics, kl_div),
        }

    except Exception as e:
        import traceback
        print(f"Error in drift analysis: {e}")
        print(traceback.format_exc())
        return {
            "drift_analysis": {
                "error": str(e),
                "combined_drift_score": 0.0,
                "avg_centroid_distance": 0.0,
                "max_centroid_distance": 0.0,
                "kl_divergence": 0.0,
                "drift_detected": False,
                "drift_level": "error",
            },
            "interpretation": {
                "drift_detected": "false",
                "drift_level": "error",
                "recommendation": f"Error during analysis: {str(e)}",
            },
            "human_explanation": f"Drift analysis failed: {str(e)}",
        }


def _get_drift_recommendation(drift_level: str, feature_drifts: List[Dict[str, Any]]) -> str:
    """Generate recommendation based on drift level and features."""
    if drift_level == "high":
        return "IMMEDIATE ACTION REQUIRED: Significant data drift detected. Retrain model with recent data to maintain accuracy."
    elif drift_level == "medium":
        drifted_features = [f['feature'] for f in feature_drifts[:3] if f['drift_detected']]
        if drifted_features:
            return f"Moderate drift in: {', '.join(drifted_features)}. Schedule model retraining."
        return "Moderate feature drift detected. Monitor closely and consider retraining within 30 days."
    else:
        return "Model is stable. Continue regular monitoring."


def _format_drift_explanation(n_samples: int, drift_level: str, combined_score: float,
                              feature_drifts: List[Dict[str, Any]],
                              centroid_metrics: Dict[str, float], kl_div: float) -> str:
    """Format human-readable drift explanation."""
    severity_words = {
        "high": "significant",
        "medium": "moderate",
        "low": "minimal"
    }

    explanation = f"Drift analysis of {n_samples} samples shows {severity_words[drift_level]} distribution shift (combined score: {combined_score:.3f}). "

    # Top drifted features
    drifted = [f for f in feature_drifts[:3] if f['drift_detected']]
    if drifted:
        feature_names = [f"{f['feature']} (z={f['z_score']:.1f})" for f in drifted]
        explanation += f"Primary drift indicators: {', '.join(feature_names)}. "

    # Statistical summary
    explanation += f"Centroid deviation: {centroid_metrics['avg_centroid_distance']:.3f}. KL divergence: {kl_div:.4f}. "

    if drift_level == "high":
        explanation += "Model retraining strongly recommended to maintain predictive performance."
    elif drift_level == "medium":
        explanation += "Schedule model review and consider retraining within 30 days."
    else:
        explanation += "No immediate action required; model remains well-calibrated."

    return explanation


def _empty_drift_result():
    return {
        "drift_analysis": {
            "avg_centroid_distance": 0.0,
            "max_centroid_distance": 0.0,
            "kl_divergence": 0.0,
            "drift_detected": False,
            "drift_level": "low",
            "train_distribution": [],
            "new_distribution": [],
        },
        "interpretation": {
            "drift_detected": "false",
            "drift_level": "low",
            "kl_divergence": "0.0",
            "avg_centroid_shift": "0.0",
            "recommendation": "No data available for drift analysis",
        },
        "human_explanation": "No data available for drift analysis. Please provide applicant data to monitor model drift.",
    }
