import {
  // Core data types
  ApplicantData,
  ClientData,
  // Credit scoring types
  PredictionResult,
  SimilarApplicantsResult,
  ExplainDenialResult,
  ThinFileResult,
  DriftResult,
  PeerGroupsResult,
  ModelInfo,
  CreditScoreResponse,
  // Fraud detection types
  FraudSimilarResult,
  FraudRingsResult,
  FraudScanStatus,
  // Policy types
  PolicyDecisionRequest,
  PolicyDecisionResult,
  // Orchestrator types
  LoanApplicationRequest,
  LoanApplicationResponse,
  // Enrichment types
  EnrichmentResult,
  // Report types
  ReportRequest,
  ReportResponse,
  ReportStatus,
  // Combined types
  EnrichedSimilarResult,
  EnrichedSimilarApplicant,
  // Synthetic data types
  SyntheticDataRequest,
  SyntheticDataResponse,
  QualityMetrics,
  SyntheticRecord,
  // Causal inference types
  CausalAnalysisRequest,
  CausalAnalysisResult,
  TreatmentEffect,
  CounterfactualOutcome,
  PropensityScore,
  // Social capital types
  SocialCapitalRequest,
  SocialCapitalResponse,
  SocialMetrics,
  NetworkData,
  NetworkNode,
  NetworkEdge,
  NetworkAnalysisRequest,
  NetworkAnalysisResult,
  // Combined score types
  CombinedScoreResult,
  EnhancedPredictionRequest,
  // Agentic types
  AgenticAnalysisResult,
  AgenticReportResult,
  // Insights types
  InsightsResult,
  NetworkResult,
} from "./types";

export type {
  // Core
  ApplicantData,
  ClientData,
  // Credit Scoring
  PredictionResult,
  RiskFactor,
  SimilarApplicantsResult,
  ExplainDenialResult,
  ThinFileResult,
  DriftResult,
  PeerGroupsResult,
  ModelInfo,
  CreditScoreResponse,
  // Fraud Detection
  FraudSimilarResult,
  FraudSimilarApplicant,
  FraudRingsResult,
  FraudScanStatus,
  // Policy
  PolicyDecisionRequest,
  PolicyDecisionResult,
  // Orchestrator
  LoanApplicationRequest,
  LoanApplicationResponse,
  // Enrichment
  EnrichmentResult,
  // Reports
  ReportRequest,
  ReportResponse,
  ReportStatus,
  // Combined
  EnrichedSimilarResult,
  EnrichedSimilarApplicant,
  // Synthetic
  SyntheticDataRequest,
  SyntheticDataResponse,
  QualityMetrics,
  SyntheticRecord,
  SparklineDataPoint,
  // Causal Inference
  CausalAnalysisRequest,
  CausalAnalysisResult,
  TreatmentEffect,
  CounterfactualOutcome,
  PropensityScore,
  // Social Capital
  SocialCapitalRequest,
  SocialCapitalResponse,
  SocialMetrics,
  NetworkData,
  NetworkNode,
  NetworkEdge,
  NetworkAnalysisRequest,
  NetworkAnalysisResult,
  // Combined Score
  CombinedScoreResult,
  EnhancedPredictionRequest,
  // Agentic
  AgenticAnalysisResult,
  AgenticReportResult,
  AgentData,
  BehavioralRiskAgent,
  FinancialRiskAgent,
  GovernanceRiskAgent,
  CompositeRiskAgent,
  ConsensusArbitrationAgent,
  SafetySupervisionAgent,
  // Insights
  InsightsResult,
  NetworkResult,
} from "./types";

const API_BASE_URL = "http://localhost:4000";

// ============== Shared Base Client ==============

class BaseClient {
  protected baseUrl: string;
  private pathPrefix: string;

  constructor(baseUrl: string = API_BASE_URL, pathPrefix: string = "") {
    this.baseUrl = baseUrl;
    this.pathPrefix = pathPrefix;
  }

  protected async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${this.pathPrefix}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers },
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API Error: ${response.statusText}`);
    }
    return response.json();
  }
}

// ============== Credit Scoring Service Client ==============

class ApiClient extends BaseClient {
  async healthCheck() {
    return this.request<{ status: string; model_loaded: boolean; faiss_index_loaded: boolean }>("/health");
  }
  async predict(data: ApplicantData): Promise<PredictionResult> {
    return this.request("/client-predict", { method: "POST", body: JSON.stringify(data) });
  }
  async findSimilarApplicants(data: ApplicantData, k: number = 10): Promise<SimilarApplicantsResult> {
    return this.request(`/similar-applicants?k=${k}`, { method: "POST", body: JSON.stringify(data) });
  }
  async explainDenial(data: ApplicantData, k: number = 20): Promise<ExplainDenialResult> {
    return this.request(`/explain-denial?k=${k}`, { method: "POST", body: JSON.stringify(data) });
  }
  async thinFilePredict(data: ApplicantData, k: number = 5): Promise<ThinFileResult> {
    return this.request(`/thin-file-predict?k=${k}`, { method: "POST", body: JSON.stringify(data) });
  }
  async monitorDrift(data: ApplicantData[], nClusters: number = 10): Promise<DriftResult> {
    return this.request(`/monitor-drift?n_clusters=${nClusters}`, { method: "POST", body: JSON.stringify(data) });
  }
  async peerGroups(data: ApplicantData[], nClusters: number = 5): Promise<PeerGroupsResult> {
    return this.request(`/peer-groups?n_clusters=${nClusters}`, { method: "POST", body: JSON.stringify(data) });
  }
  async getModelInfo() {
    return this.request<{ model_type: string; features_count: number; features: string[]; faiss_index_size: number; description: string }>("/model-info");
  }

  // Generate trend data for sparklines
  private generateTrendData(distance: number): { value: number }[] {
    return Array.from({ length: 8 }, (_, i) => ({
      value: Math.max(
        0.1,
        1 - distance - i * 0.05 + Math.random() * 0.1
      ),
    }));
  }

  // Helper to determine risk level based on distance
  private getRiskLevel(distance: number): "high" | "medium" | "low" {
    const similarity = 1 - distance;
    if (similarity >= 0.75) return "high";
    if (similarity >= 0.5) return "medium";
    return "low";
  }

  // Merge results from both endpoints with proper weighting
  private mergeSimilarResults(
    fraud: FraudSimilarResult,
    credit?: SimilarApplicantsResult
  ): EnrichedSimilarApplicant[] {
    const merged = new Map<number, EnrichedSimilarApplicant>();

    // Add fraud results with base weight
    fraud.similar_applicants.forEach((app) => {
      const similarityScore = Math.max(0, 1 - app.distance);
      merged.set(app.index, {
        index: app.index,
        distance: app.distance,
        similarityScore,
        riskLevel: this.getRiskLevel(app.distance),
        trendData: this.generateTrendData(app.distance),
        sources: ['fraud'],
        defaultLabel: app.default ?? false,
      });
    });

    // Merge credit results if available
    if (credit?.similar_applicants) {
      const creditSimilar = credit.similar_applicants;
      const indices = creditSimilar.similar_indices ?? [];
      const distances = creditSimilar.distances ?? [];
      const labels = creditSimilar.default_labels ?? [];

      indices.forEach((idx: number, i: number) => {
        const distance = distances[i] ?? 1.0;
        const existing = merged.get(idx);
        const similarityScore = Math.max(0, 1 - distance);

        if (existing) {
          // Combine scores: average the similarity, prefer lower distance
          existing.similarityScore = (existing.similarityScore + similarityScore) / 2;
          existing.distance = Math.min(existing.distance, distance);
          existing.sources = [...(existing.sources ?? []), 'credit'];
          if (labels[i] !== undefined) {
            existing.defaultLabel = labels[i] === 1;
          }
        } else {
          merged.set(idx, {
            index: idx,
            distance,
            similarityScore,
            riskLevel: this.getRiskLevel(distance),
            trendData: this.generateTrendData(distance),
            sources: ['credit'],
            defaultLabel: labels[i] === 1,
          });
        }
      });
    }

    // Sort by combined similarity score (descending)
    return Array.from(merged.values())
      .sort((a, b) => b.similarityScore - a.similarityScore)
      .slice(0, 10); // Return top 10
  }

  // Fraud detection similar endpoint
  async findSimilarFraud(data: ApplicantData, k: number = 10): Promise<FraudSimilarResult> {
    return this.request<FraudSimilarResult>(`/similar?k=${k}`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Score endpoint for orchestrator integration
  async score(applicant: ClientData & Partial<ApplicantData>, useRgcn: boolean = true): Promise<CreditScoreResponse> {
    return this.request("/score", {
      method: "POST",
      body: JSON.stringify({ applicant, use_rgcn: useRgcn }),
    });
  }

  // Batch prediction
  async batchPredict(applicants: ApplicantData[]): Promise<PredictionResult[]> {
    return this.request("/batch-predict", {
      method: "POST",
      body: JSON.stringify({ applicants }),
    });
  }

  // Causal inference analysis endpoint
  async causalAnalysis(applicantId: string, data: ApplicantData): Promise<{
    applicant_id: string;
    propensity_score: number;
    recommended_decision: string;
    confidence: number;
    treatment_effects: TreatmentEffect[];
    counterfactuals: CounterfactualOutcome[];
  }> {
    return this.request(`/causal-analysis/${applicantId}`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Social capital score endpoint
  async socialScore(applicantId: string, data?: ApplicantData): Promise<{
    entity_id: string;
    entity_type: string;
    social_credit_score: number;
    network_size: number;
    connection_count: number;
    risk_indicators: {
      fraud_risk: number;
      default_risk: number;
      reputational_risk: number;
    };
    analysis_summary: string;
  }> {
    return this.request(`/social-score/${applicantId}`, {
      method: "POST",
      body: JSON.stringify(data || {}),
    });
  }

  // Combined prediction with ML + Causal + Social features
  async combinedScore(data: ApplicantData & { include_causal?: boolean; include_social?: boolean; applicant_id?: string }): Promise<CombinedScoreResult> {
    return this.request<CombinedScoreResult>("/combined-score", {
      method: "POST",
      body: JSON.stringify({
        applicant_data: data,
        include_causal: data.include_causal ?? true,
        include_social: data.include_social ?? true,
        applicant_id: data.applicant_id,
      }),
    });
  }

  // Enhanced prediction endpoint
  async predictEnhanced(data: EnhancedPredictionRequest): Promise<CombinedScoreResult> {
    return this.request<CombinedScoreResult>("/predict-enhanced", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Combined similar endpoint - calls both fraud and credit scoring in parallel
  async findSimilarCombined(
    data: ApplicantData,
    k: number = 10
  ): Promise<EnrichedSimilarResult> {
    const [fraud, credit] = await Promise.all([
      this.request<FraudSimilarResult>(`/similar?k=${k}`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
      this.request<SimilarApplicantsResult>(`/similar-applicants?k=${k}`, {
        method: "POST",
        body: JSON.stringify(data),
      }).catch(() => undefined), // Graceful fallback
    ]);

    return {
      fraudSimilar: fraud,
      creditSimilar: credit,
      combined: this.mergeSimilarResults(fraud, credit),
    };
  }

  // ============== Causal Inference Endpoints ==============

  async getCausalAnalysis(applicantId: string): Promise<import("./types").CausalAnalysisResult> {
    return this.request(`/causal/analysis/${applicantId}`);
  }

  async getSocialScore(applicantId: string): Promise<import("./types").SocialCapitalResponse> {
    return this.request(`/social/score/${applicantId}`);
  }

  async getNetworkData(applicantId: string, depth: number = 2): Promise<import("./types").NetworkData> {
    return this.request(`/social/network/${applicantId}?depth=${depth}`);
  }

  async getCombinedScore(data: ApplicantData & { applicant_id: string }): Promise<{
    credit_score: import("./types").CreditScoreResponse;
    social_score: import("./types").SocialCapitalResponse;
    causal_analysis: import("./types").CausalAnalysisResult;
    combined_risk: number;
    recommendation: string;
  }> {
    return this.request("/combined/score", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}

// Synthetic Data Service Client (routes through API Gateway)
class SyntheticDataClient extends BaseClient {
  constructor() {
    super(API_BASE_URL, "/synthetic");
  }

  async healthCheckSynthetic(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/health");
  }

  async generateSyntheticData(data: SyntheticDataRequest): Promise<SyntheticDataResponse> {
    return this.request<SyntheticDataResponse>("/generate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}

// ============== Orchestrator Service Client ==============

class OrchestratorClient extends BaseClient {

  /**
   * Submit a new loan application
   * Returns application ID for tracking
   */
  async submitApplication(request: LoanApplicationRequest): Promise<LoanApplicationResponse> {
    return this.request("/apply", { method: "POST", body: JSON.stringify(request) });
  }

  /**
   * Get application status and results
   */
  async getApplication(appId: string): Promise<LoanApplicationResponse> {
    return this.request(`/applications/${appId}`);
  }

  /**
   * Poll application until complete
   */
  async pollApplication(
    appId: string,
    onUpdate?: (app: LoanApplicationResponse) => void,
    maxAttempts = 60,
    intervalMs = 1000
  ): Promise<LoanApplicationResponse> {
    for (let i = 0; i < maxAttempts; i++) {
      const app = await this.getApplication(appId);
      onUpdate?.(app);
      if (app.status === "approve" || app.status === "deny" || app.status === "error") {
        return app;
      }
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
    throw new Error("Application polling timeout");
  }
}

// ============== Policy Service Client ==============

class PolicyClient extends BaseClient {

  /**
   * Evaluate credit policy decision
   */
  async evaluate(request: PolicyDecisionRequest): Promise<PolicyDecisionResult> {
    return this.request("/evaluate", { method: "POST", body: JSON.stringify(request) });
  }
}

// ============== Data Enrichment Service Client ==============

class EnrichmentClient extends BaseClient {

  /**
   * Enrich applicant data with bureau and banking data
   */
  async enrich(data: ClientData): Promise<EnrichmentResult> {
    return this.request("/enrich", { method: "POST", body: JSON.stringify(data) });
  }
}

// ============== Fraud Detection Service Client ==============

class FraudDetectionClient extends BaseClient {

  /**
   * Find similar applicants (fraud detection)
   */
  async findSimilar(data: ApplicantData, k: number = 10): Promise<FraudSimilarResult> {
    return this.request(`/similar?k=${k}`, { method: "POST", body: JSON.stringify(data) });
  }

  /**
   * Get detected fraud rings
   */
  async getFraudRings(): Promise<FraudRingsResult> {
    return this.request("/fraud-rings");
  }

  /**
   * Get fraud scan status
   */
  async getScanStatus(): Promise<FraudScanStatus> {
    return this.request("/fraud-rings/status");
  }
}

// ============== Report Generator Service Client ==============

class ReportClient extends BaseClient {

  /**
   * Generate a credit report
   */
  async generate(request: ReportRequest): Promise<ReportResponse> {
    return this.request("/generate", { method: "POST", body: JSON.stringify(request) });
  }

  /**
   * Get report status and content
   */
  async getReport(reportId: string): Promise<ReportStatus> {
    return this.request(`/reports/${reportId}`);
  }

  /**
   * Poll report generation until complete
   */
  async pollReport(
    reportId: string,
    onUpdate?: (status: ReportStatus) => void,
    maxAttempts = 30,
    intervalMs = 500
  ): Promise<ReportStatus> {
    for (let i = 0; i < maxAttempts; i++) {
      const status = await this.getReport(reportId);
      onUpdate?.(status);
      if (status.status === "completed") {
        return status;
      }
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
    throw new Error("Report generation timeout");
  }
}

// ============== Causal Inference Service Client ==============

class CausalInferenceClient extends BaseClient {

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/health");
  }

  async estimatePropensity(applicantId: string, features: Record<string, number>): Promise<{
    applicant_id: string;
    propensity_score: number;
    treatment_probability: number;
    risk_tier: string;
  }> {
    return this.request("/estimate-propensity", {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId, features }),
    });
  }

  async estimateTreatmentEffect(applicantId: string, features: Record<string, number>, treatment: string): Promise<{
    applicant_id: string;
    treatment: string;
    effects: TreatmentEffect[];
  }> {
    return this.request("/estimate-treatment-effect", {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId, features, treatment, method: "all" }),
    });
  }

  async generateCounterfactuals(applicantId: string, features: Record<string, number>): Promise<{
    applicant_id: string;
    scenarios: CounterfactualOutcome[];
    optimal_decision: string;
  }> {
    return this.request("/counterfactuals", {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId, features }),
    });
  }

  async upliftModeling(applicantId: string, features: Record<string, number>): Promise<{
    applicant_id: string;
    uplift_score: number;
    segment: string;
    recommendation: string;
  }> {
    return this.request("/uplift-modeling", {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId, features }),
    });
  }

  async fullAnalysis(applicantId: string, features: Record<string, number>): Promise<CausalAnalysisResult> {
    return this.request("/analyze", {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId, features }),
    });
  }
}

// ============== Social Capital Service Client ==============

class SocialCapitalClient extends BaseClient {

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/health");
  }

  async calculate(request: SocialCapitalRequest): Promise<SocialCapitalResponse> {
    return this.request("/calculate", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async getVisualizationData(entityId: string, depth: number = 2): Promise<NetworkData> {
    return this.request("/visualization-data", {
      method: "POST",
      body: JSON.stringify({ entity_id: entityId, entity_type: "individual", depth }),
    });
  }

  async analyzeNetwork(nodes: NetworkNode[], edges: NetworkEdge[]): Promise<NetworkAnalysisResult> {
    return this.request("/network-analysis", {
      method: "POST",
      body: JSON.stringify({ nodes, edges, analysis_type: "full" }),
    });
  }

  async getRiskIndicators(entityId: string): Promise<{
    fraud_risk: number;
    default_risk: number;
    reputational_risk: number;
  }> {
    return this.request(`/risk-indicators?entity_id=${entityId}`);
  }
}

// ============== Combined/Unified Service Client ==============

// ============== Simplified Unified Augmented Scoring Client ==============

class AugmentedScoringClient extends BaseClient {
  constructor(baseUrl: string = "http://localhost:8008") {
    super(baseUrl);
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>("/health");
  }

  async getScore(applicantId: string, features: ApplicantData): Promise<{
    applicant_id: string;
    base_ml: { default_probability: number; risk_level: string };
    combined_risk_score: number;
    combined_risk_level: string;
    combined_decision: string;
    feature_weights: { ml_weight: number; causal_weight: number; social_weight: number };
    explanation: string;
  }> {
    return this.request("/score", {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId, features }),
    });
  }

  async getInsights(applicantId: string, features: ApplicantData): Promise<InsightsResult> {
    return this.request("/insights", {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId, features }),
    });
  }

  async getNetwork(entityId: string): Promise<NetworkResult> {
    return this.request(`/network/${entityId}`);
  }

  // ============== CreditXAI Multi-Agent Endpoints ==============

  async getAgenticAnalysis(
    applicantId: string,
    features: ApplicantData,
    includeHistory: boolean = true
  ): Promise<AgenticAnalysisResult> {
    return this.request("/agents/analyze", {
      method: "POST",
      body: JSON.stringify({
        applicant_id: applicantId,
        features,
        include_history: includeHistory,
      }),
    });
  }

  async getAgentReport(
    applicantId: string,
    features: ApplicantData,
    analysis: AgenticAnalysisResult
  ): Promise<AgenticReportResult> {
    return this.request(`/agents/report/${applicantId}`, {
      method: "POST",
      body: JSON.stringify({ features, analysis }),
    });
  }
}

// ============== Exports ==============
export { BaseClient };
export const api = new ApiClient();
export const syntheticDataApi = new SyntheticDataClient();
export const orchestratorApi = new OrchestratorClient();
export const policyApi = new PolicyClient();
export const enrichmentApi = new EnrichmentClient();
export const fraudDetectionApi = new FraudDetectionClient();
export const reportApi = new ReportClient();
export const causalInferenceApi = new CausalInferenceClient();
export const socialCapitalApi = new SocialCapitalClient();
export const augmentedScoringApi = new AugmentedScoringClient();