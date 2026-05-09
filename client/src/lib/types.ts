// ============== Core Data Types ==============

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

export interface ClientData {
  client_id: string;
  name: string;
  email: string;
  ssn: string;
  phone: string;
  address: string;
}

// ============== Credit Scoring Types ==============

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

export interface CreditScoreResponse {
  base_probability: number;
  risk_grade?: string;
  decision?: string;
  interest_rate?: number;
  recommended_max_amount?: number;
  explanation?: string;
}

export interface SimilarApplicantData {
  similar_indices: number[];
  distances: number[];
  default_labels: number[];
  default_count: number;
  total_similar: number;
  default_rate: number;
  risk_assessment: string;
}

export interface SimilarApplicantsResult {
  applicant: ApplicantData;
  similar_applicants: SimilarApplicantData;
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

export interface ModelInfo {
  model_type: string;
  features_count: number;
  features: string[];
  faiss_index_size: number;
  description: string;
}

// Fraud Detection Similar Result Types
export interface FraudSimilarApplicant {
  index: number;
  distance: number;
  similarityScore: number; // Converted: 1 - distance
  default?: boolean;
}

export interface FraudSimilarResult {
  similar_applicants: FraudSimilarApplicant[];
  total: number;
}

export interface FraudRing {
  id: string;
  members: number[];
  risk_score: number;
  detected_at: string;
}

export interface FraudRingsResult {
  total_rings: number;
  rings: FraudRing[];
  status: string;
}

export interface FraudScanStatus {
  last_scan_time: string | null;
  is_scanning: boolean;
  fraud_rings_detected: number;
}

// ============== Policy Types ==============

export interface PolicyDecisionRequest {
  risk_score: number;
  monthly_income?: number;
  debt_ratio?: number;
  employment_months?: number;
  recent_inquiries?: number;
  requested_amount: number;
}

export interface PolicyDecisionResult {
  decision: "approve" | "deny" | "review";
  risk_grade: string;
  interest_rate: number;
  recommended_max_amount: number;
  rationale: string;
}

// ============== Orchestrator Types ==============

export interface LoanApplicationRequest {
  applicant: ClientData;
  requested_amount: number;
}

export interface LoanApplicationResponse {
  application_id: string;
  status: "pending" | "processing" | "approve" | "deny" | "review" | "error";
  steps: {
    enrichment: "pending" | "running" | "complete" | "error";
    credit_scoring: "pending" | "running" | "complete" | "error";
    fraud_check: "pending" | "running" | "complete" | "error";
    policy: "pending" | "running" | "complete" | "error";
  };
  enrichment?: EnrichmentResult;
  score?: CreditScoreResponse;
  fraud?: FraudSimilarResult;
  policy?: PolicyDecisionResult;
  error?: string;
  created_at: string;
  completed_at?: string;
}

// ============== Data Enrichment Types ==============

export interface CreditBureauData {
  bureau_score: number;
  tradelines: number;
  inquiries_6m: number;
  public_records: number;
}

export interface OpenBankingData {
  avg_balance: number;
  transaction_count_3m: number;
  overdraft_count: number;
  income_estimate: number;
}

export interface EnrichmentResult {
  applicant_id: string;
  credit_bureau_data: CreditBureauData;
  open_banking_data: OpenBankingData;
  status: string;
}

// ============== Report Generator Types ==============

export interface ReportRequest {
  applicant_name: string;
  score: number;
  risk_level: string;
  decision: string;
}

export interface ReportResponse {
  report_id: string;
  status: "pending" | "generating" | "completed";
}

export interface ReportStatus {
  report_id: string;
  status: "pending" | "generating" | "completed";
  content?: string;
  created_at: string;
  completed_at?: string;
}

// ============== Utility Types ==============

// Sparkline data point for mini charts
export interface SparklineDataPoint {
  value: number;
}

// Combined enriched similar result
export interface EnrichedSimilarApplicant {
  index: number;
  distance: number;
  similarityScore: number;
  riskLevel: "high" | "medium" | "low";
  trendData: SparklineDataPoint[];
  sources?: string[];  // Which services found this applicant ('fraud', 'credit')
  defaultLabel?: boolean;  // Whether this applicant defaulted
}

export interface EnrichedSimilarResult {
  fraudSimilar: FraudSimilarResult;
  creditSimilar?: SimilarApplicantsResult;
  combined: EnrichedSimilarApplicant[];
}

// ============== Combined Feature Types ==============

export interface ApplicationWorkflowResult {
  application: LoanApplicationResponse;
  enrichment?: EnrichmentResult;
  creditScore?: CreditScoreResponse;
  fraudCheck?: FraudSimilarResult;
  policy?: PolicyDecisionResult;
}

export interface FullAnalysisResult {
  prediction: PredictionResult;
  similarApplicants: SimilarApplicantsResult;
  fraudSimilar: FraudSimilarResult;
  enrichment?: EnrichmentResult;
  policy?: PolicyDecisionResult;
}

// Synthetic Data Types
export interface QualityMetrics {
  similarity_score: number;
  privacy_score: number;
  validity_score: number;
  overall_score: number;
}

export interface SyntheticRecord {
  [key: string]: number | string | null;
}

export interface SyntheticDataRequest {
  num_records: number;
  apply_constraints?: boolean;
  random_seed?: number | null;
}

export interface SyntheticDataResponse {
  num_records: number;
  records: SyntheticRecord[];
  quality_metrics: QualityMetrics;
  generated_at: string;
}

// ============== Causal Inference Types ==============

export interface CausalAnalysisRequest {
  applicant_id: string;
  treatment_variable?: string;
  covariates?: string[];
  outcome_variable?: string;
}

export interface TreatmentEffect {
  estimate: number;
  confidence_interval: [number, number];
  p_value: number;
  standard_error: number;
  method: "propensity_matching" | "doubly_robust" | "cluster_adjusted";
  significance: "significant" | "not_significant";
}

export interface CounterfactualOutcome {
  scenario: string;
  treatment_value: number;
  expected_outcome: number;
  outcome_change: number;
  risk_impact: "increase" | "decrease" | "neutral";
}

export interface PropensityScore {
  bin: string;
  treated_count: number;
  control_count: number;
  treated_pct: number;
  control_pct: number;
  balance_ratio: number;
}

export interface CausalAnalysisResult {
  applicant_id: string;
  treatment_effect: TreatmentEffect;
  propensity_scores: PropensityScore[];
  counterfactuals: CounterfactualOutcome[];
  covariate_balance: Record<string, { before: number; after: number }>;
  interpretation: {
    causal_impact: string;
    recommendation: string;
    confidence_level: string;
  };
}

// ============== Social Capital Types ==============

export interface NetworkNode {
  id: string;
  label: string;
  type: "individual" | "organization" | "business" | "influencer";
  centrality_score: number;
  influence_score: number;
  trust_score: number;
  community_count: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
  relationship: "friend" | "colleague" | "family" | "business" | "influencer";
}

export interface SocialMetrics {
  centrality: number;
  influence: number;
  trust: number;
  reach: number;
  engagement: number;
  communities: number;
}

export interface SocialCapitalRequest {
  entity_id: string;
  entity_type?: "individual" | "organization" | "business";
  depth?: number;
}

export interface SocialCapitalResponse {
  entity_id: string;
  entity_type: string;
  scores: SocialMetrics;
  network_size: number;
  connection_count: number;
  risk_indicators: {
    fraud_risk: number;
    default_risk: number;
    reputational_risk: number;
  };
  analysis_summary: string;
}

export interface NetworkData {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  entity_id: string;
  total_nodes: number;
  total_edges: number;
  communities: number;
}

export interface NetworkAnalysisRequest {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  analysis_type: "centrality" | "community" | "influence" | "full";
}

export interface NetworkAnalysisResult {
  centrality_scores: Record<string, number>;
  community_assignments: Record<string, number>;
  influence_scores: Record<string, number>;
  network_density: number;
  average_clustering: number;
  recommendations: string[];
}

// ============== Combined Score Types ==============

export interface CombinedScoreResult {
  applicant_id: string;
  ml_probability: number;
  ml_risk_level: string;
  causal_recommendation: string;
  causal_confidence: number;
  social_credit_score: number;
  social_risk_indicator: number;
  combined_probability: number;
  combined_risk_level: string;
  explanation: string;
}

export interface EnhancedPredictionRequest {
  applicant_data: ApplicantData;
  include_causal?: boolean;
  include_social?: boolean;
  applicant_id?: string;
}

// ============== Agentic Analysis Types ==============

export interface AgentData {
  agent: string;
  risk_score?: number;
  risk_level?: string;
  composite_score?: number;
  rating?: string;
  confidence?: number;
}

export interface BehavioralRiskAgent extends AgentData {
  agent: string;
  risk_score: number;
  risk_level: string;
  analysis: string;
}

export interface FinancialRiskAgent extends AgentData {
  agent: string;
  risk_score: number;
  financial_health: string;
  key_metrics: {
    revolving_utilization: string;
    debt_ratio: string;
    monthly_income: string;
    age: number;
    late_payments_90d: number;
    open_credit_lines: number;
  };
}

export interface GovernanceRiskAgent extends AgentData {
  agent: string;
  trust_score: number;
  fraud_risk: number;
  reputational_risk: number;
  network_connections: number;
}

export interface CompositeRiskAgent extends AgentData {
  agent: string;
  composite_score: number;
  rating: string;
  method: string;
}

export interface ConsensusArbitrationAgent extends AgentData {
  agent: string;
  consensus_decision: string;
  confidence: number;
  risk_consensus: string[];
  rationale: string;
}

export interface SafetySupervisionAgent extends AgentData {
  agent: string;
  validation_passed: boolean;
  quality_score: number;
  traceability: string[];
  anomalies_detected: string[];
}

export interface AgenticAnalysisResult {
  applicant_id: string;
  timestamp: string;
  agents: {
    bra: BehavioralRiskAgent;
    fra: FinancialRiskAgent;
    gra: GovernanceRiskAgent;
    cra: CompositeRiskAgent;
  };
  caa: ConsensusArbitrationAgent;
  ssa: SafetySupervisionAgent;
  history_aware: boolean;
  causal_insights: {
    propensity_tier: string;
    optimal_decision: string;
    counterfactuals_count: number;
  };
  recommendation: string;
  confidence: number;
  combined_risk_score: number;
}

export interface AgenticReportResult {
  report_id: string;
  generated_at: string;
  applicant_id: string;
  executive_summary: {
    rating: string;
    outlook: string;
    recommendation: string;
    key_factors: string[];
  };
  risk_assessment: {
    business_risk: string;
    financial_risk: string;
    governance_risk: string;
  };
  agent_consensus: {
    bra_score: number;
    fra_score: number;
    gra_score: number;
    caa_decision: string;
  };
  methodology: string;
  confidence_level: string;
  risk_breakdown?: {
    ml_weight: number;
    causal_weight: number;
    social_weight: number;
  };
  combined_risk_score?: number;
}

// ============== Insights Types ==============

export interface CounterfactualInsight {
  decision: string;
  probability: number;
  change: number;
}

export interface InsightsResult {
  applicant_id: string;
  ml_risk: number;
  ml_risk_level: string;
  propensity_score: number;
  causal_recommendation: string;
  optimal_decision: string;
  expected_improvement: number;
  counterfactuals: CounterfactualInsight[];
  social_trust: number;
  social_influence: number;
  social_network_size: number;
  social_connections: number;
  fraud_risk: number;
  social_credit_score: number;
  recommendation: string;
  confidence: number;
  summary: string;
}

export interface NetworkResult {
  nodes: Array<{ id: string; label: string; type: string; x: number; y: number }>;
  edges: Array<{ source: string; target: string; weight: number }>;
  communities: number;
}

// ============== Generic Utility Types ==============

export interface ApiResponse<T> {
  data: T;
  status: "success" | "error";
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}