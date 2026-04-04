export interface ApplicantData {
  RevolvingUtilizationOfUnsecuredLines: number;
  age: number;
  NumberOfTime30_59DaysPastDueNotWorse: number;
  DebtRatio: number;
  MonthlyIncome: number;
  NumberOfOpenCreditLinesAndLoans: number;
  NumberOfTimes90DaysLate: number;
  NumberRealEstateLoansOrLines: number;
  NumberOfTime60_89DaysPastDueNotWorse: number;
  NumberOfDependents: number;
}

export interface RiskFactor {
  feature: string;
  shap_value: number;
  impact: "increases_risk" | "decreases_risk";
}

export interface PredictionResult {
  prediction: number;
  default_probability: number;
  risk_level: "low" | "medium" | "high";
  message: string;
  top_risk_factors: RiskFactor[];
}

export interface SimilarApplicantsResult {
  applicant: ApplicantData;
  similar_applicants: {
    similar_indices: number[];
    distances: number[];
    default_labels: number[];
    default_count: number;
    total_similar: number;
    default_rate: number;
    risk_assessment: string;
  };
  interpretation: { default_rate: string; risk_assessment: string; summary: string };
  human_explanation: string;
}

export interface ExplainDenialResult {
  prediction: string;
  default_probability: number;
  denial_reasons: RiskFactor[];
  similar_approved_applicants: {
    count: number;
    counter_examples: Array<{ index: number; distance: number; features: Record<string, number> }>;
  };
  explanation: string;
  recommendation: string;
  human_explanation: string;
}

export interface ThinFileResult {
  base_prediction: { probability: number; prediction: number };
  neighbor_features: {
    neighbor_default_rate: number;
    avg_neighbor_distance: number;
    min_neighbor_distance: number;
    weighted_neighbor_risk: number;
    neighbor_count: number;
  };
  enhanced_prediction: { probability: number; prediction: number; neighbor_weight_applied: number; distance_confidence: number };
  interpretation: { thin_file_detected: boolean; neighbor_risk_level: string; summary: string };
  human_explanation: string;
}

export interface DriftResult {
  drift_analysis: {
    avg_centroid_distance: number;
    max_centroid_distance: number;
    kl_divergence: number;
    drift_detected: boolean;
    drift_level: "low" | "medium" | "high";
    train_distribution: number[];
    new_distribution: number[];
  };
  interpretation: { drift_detected: boolean; drift_level: string; kl_divergence: string; avg_centroid_shift: string; recommendation: string };
  human_explanation: string;
}

export interface PeerGroupsResult {
  total_customers: number;
  n_segments: number;
  segments: Array<{ segment: string; size: number; percentage: string; default_rate: string; risk_level: string; profile: Record<string, number> }>;
  summary: { highest_risk_segment: string | null; lowest_risk_segment: string | null };
  human_explanation: string;
}