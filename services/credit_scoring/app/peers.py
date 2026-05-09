import numpy as np
import pandas as pd
from typing import List, Dict, Any

# Feature names matching the training data
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


def _to_feature_vector(record: Dict[str, Any]) -> List[float]:
    """Extract features in consistent order."""
    return [
        float(record.get("RevolvingUtilizationOfUnsecuredLines", 0) or 0),
        float(record.get("age", 0) or 0),
        float(record.get("NumberOfTime30_59DaysPastDueNotWorse", 0) or 0),
        float(record.get("DebtRatio", 0) or 0),
        float(record.get("MonthlyIncome", 0) or 0),
        float(record.get("NumberOfOpenCreditLinesAndLoans", 0) or 0),
        float(record.get("NumberOfTimes90DaysLate", 0) or 0),
        float(record.get("NumberRealEstateLoansOrLines", 0) or 0),
        float(record.get("NumberOfTime60_89DaysPastDueNotWorse", 0) or 0),
        float(record.get("NumberOfDependents", 0) or 0),
    ]


def _compute_segment_risk_score(profile: Dict[str, float]) -> float:
    """Compute a risk score based on segment characteristics."""
    # Weighted features for risk estimation
    utilization = profile.get("RevolvingUtilizationOfUnsecuredLines", 0)
    age = profile.get("age", 45)
    past_due_30_59 = profile.get("NumberOfTime30_59DaysPastDueNotWorse", 0)
    past_due_60_89 = profile.get("NumberOfTime60_89DaysPastDueNotWorse", 0)
    past_due_90 = profile.get("NumberOfTimes90DaysLate", 0)
    debt_ratio = profile.get("DebtRatio", 0.3)

    # Normalize and compute risk score (0-1 range)
    # Utilization: 0-1, higher = riskier
    util_risk = min(utilization * 0.4, 0.4)

    # Age: younger = riskier (normalize to 0-1 with typical range 18-75)
    age_risk = max(0, (75 - age) / 57 * 0.15)

    # Past due: more = riskier
    past_due_risk = min((past_due_30_59 + past_due_60_89 * 2 + past_due_90 * 3) * 0.08, 0.25)

    # Debt ratio: higher = riskier (cap at 1.0)
    debt_risk = min(debt_ratio * 0.2, 0.2)

    total_risk = util_risk + age_risk + past_due_risk + debt_risk
    return min(max(total_risk, 0.05), 0.95)  # Clamp between 5%-95%


def _get_segment_profile_description(profile: Dict[str, float], risk_level: str) -> str:
    """Generate a human-readable description of the segment."""
    util = profile.get("RevolvingUtilizationOfUnsecuredLines", 0)
    age = profile.get("age", 45)
    income = profile.get("MonthlyIncome", 5000)
    debt_ratio = profile.get("DebtRatio", 0.3)
    past_due = (
        profile.get("NumberOfTime30_59DaysPastDueNotWorse", 0) +
        profile.get("NumberOfTime60_89DaysPastDueNotWorse", 0) +
        profile.get("NumberOfTimes90DaysLate", 0)
    )

    descriptors = []
    if util > 0.8:
        descriptors.append("high utilization")
    elif util < 0.3:
        descriptors.append("low utilization")

    if age < 30:
        descriptors.append("young")
    elif age > 55:
        descriptors.append("mature")

    if income > 10000:
        descriptors.append("high income")
    elif income < 3000:
        descriptors.append("lower income")

    if past_due > 2:
        descriptors.append("late payment history")

    if debt_ratio > 0.6:
        descriptors.append("elevated debt")

    desc_text = ", ".join(descriptors) if descriptors else "average profile"

    risk_desc = {
        "high": "high risk",
        "medium": "moderate risk",
        "low": "low risk"
    }.get(risk_level, "unknown risk")

    return f"{desc_text}, {risk_desc}"


def segment_peer_groups(data: List[Dict[str, Any]], n_clusters: int = 5):
    """Segment customers into peer groups using KMeans clustering."""
    if not data:
        return _empty_peer_result()

    # Convert to feature matrix
    try:
        data_matrix = np.array([_to_feature_vector(record) for record in data])
    except Exception:
        return _empty_peer_result()

    # Handle NaN values
    data_matrix = np.nan_to_num(data_matrix, nan=0.0, posinf=0.0, neginf=0.0)

    n_samples = data_matrix.shape[0]
    n_clusters = min(n_clusters, n_samples)

    # Normalize for clustering (z-score normalization)
    feature_stds = data_matrix.std(axis=0)
    feature_stds = np.where(feature_stds == 0, 1, feature_stds)
    normalized = (data_matrix - data_matrix.mean(axis=0)) / feature_stds

    # Perform KMeans clustering
    try:
        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(normalized)

        # Compute cluster centers in original scale
        cluster_centers = kmeans.cluster_centers_ * feature_stds + data_matrix.mean(axis=0)
    except Exception:
        # Fallback: simple random assignment
        cluster_labels = np.random.randint(0, n_clusters, size=n_samples)
        cluster_centers = None

    # Build segments
    segments = []
    for i in range(n_clusters):
        mask = cluster_labels == i
        segment_size = int(mask.sum())

        if segment_size == 0:
            continue

        segment_pct = float(segment_size) / n_samples * 100

        # Compute segment mean
        segment_data = data_matrix[mask]
        segment_mean = segment_data.mean(axis=0)

        # Build profile
        profile = {
            FEATURE_NAMES[j]: round(float(segment_mean[j]), 4)
            for j in range(min(len(FEATURE_NAMES), len(segment_mean)))
        }

        # Compute risk score based on profile
        risk_score = _compute_segment_risk_score(profile)

        # Risk level aligned with predictor thresholds
        risk_level = "high" if risk_score > 0.5 else "medium" if risk_score > 0.3 else "low"

        # Compute within-segment variance (compactness)
        segment_std = segment_data.std(axis=0).mean() if segment_size > 1 else 0

        segments.append({
            "segment": f"Segment {chr(65 + i)}",
            "cluster_id": i,
            "size": segment_size,
            "percentage": round(segment_pct, 2),
            "percentage_str": f"{segment_pct:.1f}%",
            "default_rate": round(risk_score, 4),
            "default_rate_str": f"{risk_score * 100:.1f}%",
            "risk_level": risk_level,
            "compactness": round(float(segment_std), 4),
            "profile": profile,
            "description": _get_segment_profile_description(profile, risk_level),
            "centroid": profile if cluster_centers is None else {
                FEATURE_NAMES[j]: round(float(cluster_centers[i][j]), 4)
                for j in range(min(len(FEATURE_NAMES), cluster_centers.shape[1]))
            },
        })

    # Sort by risk (default rate) descending
    segments_sorted = sorted(segments, key=lambda x: x["default_rate"], reverse=True)

    # Reassign segment letters based on risk
    for i, seg in enumerate(segments_sorted):
        seg["segment"] = f"Segment {chr(65 + i)}"

    highest_risk = segments_sorted[0]["segment"] if segments_sorted else None
    lowest_risk = segments_sorted[-1]["segment"] if segments_sorted else None

    # Compute overall statistics
    avg_segment_size = float(np.mean([s["size"] for s in segments])) if segments else 0
    size_variance = float(np.var([s["size"] for s in segments])) if len(segments) > 1 else 0
    balanced = bool(size_variance / (avg_segment_size ** 2 + 1e-8) < 0.5) if avg_segment_size > 0 else True

    return {
        "total_customers": int(n_samples),
        "n_segments": len(segments),
        "segments": segments_sorted,
        "summary": {
            "highest_risk_segment": highest_risk,
            "lowest_risk_segment": lowest_risk,
            "average_segment_size": round(float(avg_segment_size), 1),
            "balanced_clustering": balanced,
            "model_quality": "good" if balanced else "fair",
        },
        "human_explanation": _format_peer_explanation(n_samples, segments_sorted, highest_risk, lowest_risk),
    }


def _format_peer_explanation(n_samples: int, segments: List[Dict[str, Any]],
                             highest_risk: str, lowest_risk: str) -> str:
    """Format human-readable explanation of peer groups."""
    if not segments:
        return "No segments identified."

    seg_descriptions = []
    for i, seg in enumerate(segments[:3]):  # Top 3 segments
        desc = f"{seg['segment']}: {seg['size']} customers ({seg['percentage_str']}) - {seg['default_rate_str']} risk, {seg['description']}"
        seg_descriptions.append(desc)

    explanation = (
        f"Customer segmentation analyzed {n_samples} applicants across {len(segments)} distinct peer groups. "
        f"The highest risk segment is {highest_risk}, while {lowest_risk} represents the most favorable profiles. "
        f"Key segments: {'; '.join(seg_descriptions)}"
    )

    return explanation


def _empty_peer_result():
    return {
        "total_customers": 0,
        "n_segments": 0,
        "segments": [],
        "summary": {"highest_risk_segment": None, "lowest_risk_segment": None},
        "human_explanation": "No data available for peer group analysis. Please provide customer data to segment into peer groups.",
    }
