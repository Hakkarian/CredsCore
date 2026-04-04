import { ApplicantData, PredictionResult, SimilarApplicantsResult, ExplainDenialResult, ThinFileResult, DriftResult, PeerGroupsResult } from "./types";

export type { ApplicantData, PredictionResult, RiskFactor, SimilarApplicantsResult, ExplainDenialResult, ThinFileResult, DriftResult, PeerGroupsResult } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;
  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, { ...options, headers: { "Content-Type": "application/json", ...options.headers } });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API Error: ${response.statusText}`);
    }
    return response.json();
  }
  async healthCheck() {
    return this.request<{ status: string; model_loaded: boolean; faiss_index_loaded: boolean }>("/health");
  }
  async predict(data: ApplicantData): Promise<PredictionResult> {
    return this.request("/predict", { method: "POST", body: JSON.stringify(data) });
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
  async monitorDrift(data: Record<string, any>[], nClusters: number = 10): Promise<DriftResult> {
    return this.request(`/monitor-drift?n_clusters=${nClusters}`, { method: "POST", body: JSON.stringify(data) });
  }
  async peerGroups(data: Record<string, any>[], nClusters: number = 5): Promise<PeerGroupsResult> {
    return this.request(`/peer-groups?n_clusters=${nClusters}`, { method: "POST", body: JSON.stringify(data) });
  }
  async getModelInfo() {
    return this.request<{ model_type: string; features_count: number; features: string[]; faiss_index_size: number; description: string }>("/model-info");
  }
}

export const api = new ApiClient();