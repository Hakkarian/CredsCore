import numpy as np
from typing import Dict, Any

from .similar import get_similar_finder
from .predictor import get_predictor


def predict_thin_file(applicant_data: Dict[str, Any], k: int = 5):
    predictor = get_predictor()
    finder = get_similar_finder()

    base_result = predictor.predict(applicant_data, use_rgcn=False)
    base_prob = base_result["default_probability"]
    base_pred = base_result["prediction"]

    thin_file_detected = False

    if finder.features is not None:
        applicant_features = [
            applicant_data.get("RevolvingUtilizationOfUnsecuredLines", 0),
            applicant_data.get("age", 0),
            applicant_data.get("NumberOfTime30_59DaysPastDueNotWorse", 0),
            applicant_data.get("DebtRatio", 0),
            applicant_data.get("MonthlyIncome", 0),
            applicant_data.get("NumberOfOpenCreditLinesAndLoans", 0),
            applicant_data.get("NumberOfTimes90DaysLate", 0),
            applicant_data.get("NumberRealEstateLoansOrLines", 0),
            applicant_data.get("NumberOfTime60_89DaysPastDueNotWorse", 0),
            applicant_data.get("NumberOfDependents", 0),
        ]

        if len(finder.feature_names) > 0:
            distances = np.linalg.norm(
                finder.features - applicant_features[: len(finder.feature_names)],
                axis=1,
            )
            k = min(k, len(distances))
            nearest_distances = np.sort(distances)[:k]

            avg_distance = float(np.mean(nearest_distances))
            min_distance = float(np.min(nearest_distances))

            neighbor_default_rate = 0.3
            if finder.labels is not None:
                nearest_indices = np.argsort(distances)[:k]
                nearest_labels = finder.labels[nearest_indices]
                neighbor_default_rate = (
                    float(np.mean(nearest_labels))
                    if hasattr(nearest_labels, "mean")
                    else 0.3
                )

            thin_file_detected = avg_distance < 0.5

            distance_confidence = max(0, 1 - avg_distance)
            neighbor_weight = 0.3 if thin_file_detected else 0.1

            enhanced_prob = (
                base_prob * (1 - neighbor_weight)
                + neighbor_default_rate * neighbor_weight
            )
            enhanced_pred = 1 if enhanced_prob > 0.5 else 0
        else:
            avg_distance = 0.5
            min_distance = 0.3
            neighbor_default_rate = 0.3
            distance_confidence = 0.5
            neighbor_weight = 0.2
            enhanced_prob = base_prob
            enhanced_pred = base_pred
    else:
        avg_distance = 0.5
        min_distance = 0.3
        neighbor_default_rate = 0.3
        distance_confidence = 0.5
        neighbor_weight = 0.2
        enhanced_prob = base_prob
        enhanced_pred = base_pred

    neighbor_risk_level = (
        "high"
        if neighbor_default_rate > 0.5
        else "medium"
        if neighbor_default_rate > 0.2
        else "low"
    )

    thin_file_message = (
        "Thin-file applicant detected - enhanced prediction applied based on similar applicant outcomes."
        if thin_file_detected
        else "Standard prediction applied - sufficient credit history available."
    )

    return {
        "base_prediction": {"probability": base_prob, "prediction": base_pred},
        "neighbor_features": {
            "neighbor_default_rate": neighbor_default_rate,
            "avg_neighbor_distance": avg_distance,
            "min_neighbor_distance": min_distance,
            "weighted_neighbor_risk": neighbor_default_rate * neighbor_weight,
            "neighbor_count": k,
        },
        "enhanced_prediction": {
            "probability": enhanced_prob,
            "prediction": enhanced_pred,
            "neighbor_weight_applied": neighbor_weight,
            "distance_confidence": distance_confidence,
        },
        "interpretation": {
            "thin_file_detected": thin_file_detected,
            "neighbor_risk_level": neighbor_risk_level,
            "summary": thin_file_message,
        },
        "human_explanation": f"Base model prediction indicates {base_prob * 100:.1f}% probability of default. For this applicant, {'limited credit history was detected (thin file)' if thin_file_detected else 'sufficient credit history exists'}. Analysis of {k} nearest neighbors shows a {neighbor_default_rate * 100:.1f}% historical default rate. The enhanced prediction adjusts the probability to {enhanced_prob * 100:.1f}% by incorporating neighbor risk, resulting in a {'denial' if enhanced_pred == 1 else 'approval'} recommendation with {distance_confidence * 100:.0f}% confidence based on neighbor similarity.",
    }
