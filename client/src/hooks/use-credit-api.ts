import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  augmentedScoringApi,
  // API clients
  api,
  syntheticDataApi,
  orchestratorApi,
  policyApi,
  enrichmentApi,
  fraudDetectionApi,
  reportApi,
  // Types
  ApplicantData,
  ClientData,
  PredictionResult,
  SimilarApplicantsResult,
  ExplainDenialResult,
  ThinFileResult,
  DriftResult,
  PeerGroupsResult,
  ModelInfo,
  FraudSimilarResult,
  FraudRingsResult,
  FraudScanStatus,
  PolicyDecisionRequest,
  PolicyDecisionResult,
  LoanApplicationRequest,
  LoanApplicationResponse,
  EnrichedSimilarResult,
  SyntheticDataRequest,
  SyntheticDataResponse,
  ReportRequest,
  ReportResponse,
  ReportStatus,
  EnrichmentResult,
  AgenticAnalysisResult,
  AgenticReportResult,
} from "@/lib/api";

// ============================================
// CREDIT SCORING HOOKS
// ============================================

export function usePredictMutation() {
  return useMutation<PredictionResult, Error, ApplicantData>({
    mutationFn: async (data) => {
      return api.predict(data);
    },
  });
}

export function useBatchPredictMutation() {
  return useMutation<PredictionResult[], Error, ApplicantData[]>({
    mutationFn: async (applicants) => {
      return api.batchPredict(applicants);
    },
  });
}

export function useSimilarApplicantsMutation() {
  return useMutation<SimilarApplicantsResult, Error, { data: ApplicantData; k?: number }>({
    mutationFn: async ({ data, k = 10 }) => {
      return api.findSimilarApplicants(data, k);
    },
  });
}

export function useExplainDenialMutation() {
  return useMutation<ExplainDenialResult, Error, { data: ApplicantData; k?: number }>({
    mutationFn: async ({ data, k = 20 }) => {
      return api.explainDenial(data, k);
    },
  });
}

export function useThinFileMutation() {
  return useMutation<ThinFileResult, Error, { data: ApplicantData; k?: number }>({
    mutationFn: async ({ data, k = 5 }) => {
      return api.thinFilePredict(data, k);
    },
  });
}

export function useDriftMonitorMutation() {
  return useMutation<DriftResult, Error, { data: ApplicantData[]; nClusters?: number }>({
    mutationFn: async ({ data, nClusters = 10 }) => {
      return api.monitorDrift(data, nClusters);
    },
  });
}

export function usePeerGroupsMutation() {
  return useMutation<PeerGroupsResult, Error, { data: ApplicantData[]; nClusters?: number }>({
    mutationFn: async ({ data, nClusters = 5 }) => {
      return api.peerGroups(data, nClusters);
    },
  });
}

export function useModelInfo() {
  return useQuery<ModelInfo, Error>({
    queryKey: ["model-info"],
    queryFn: () => api.getModelInfo(),
  });
}

export function useHealthCheck() {
  return useQuery<{ status: string }, Error>({
    queryKey: ["health"],
    queryFn: () => api.healthCheck(),
    refetchInterval: 30000,
  });
}

// ============================================
// FRAUD DETECTION HOOKS
// ============================================

export function useFraudSimilarMutation() {
  return useMutation<FraudSimilarResult, Error, { data: ApplicantData; k?: number }>({
    mutationFn: async ({ data, k = 10 }) => {
      return fraudDetectionApi.findSimilar(data, k);
    },
  });
}

export function useFraudRingsQuery() {
  return useQuery<FraudRingsResult, Error>({
    queryKey: ["fraud-rings"],
    queryFn: () => fraudDetectionApi.getFraudRings(),
    refetchInterval: 60000,
  });
}

export function useFraudScanStatusQuery() {
  return useQuery<FraudScanStatus, Error>({
    queryKey: ["fraud-scan-status"],
    queryFn: () => fraudDetectionApi.getScanStatus(),
    refetchInterval: 30000,
  });
}

// ============================================
// COMBINED SIMILAR HOOK (CREDIT + FRAUD)
// ============================================

export function useSimilarCombinedMutation() {
  return useMutation<EnrichedSimilarResult, Error, { data: ApplicantData; k?: number }>({
    mutationFn: async ({ data, k = 10 }) => {
      return api.findSimilarCombined(data, k);
    },
  });
}

// ============================================
// SYNTHETIC DATA HOOKS
// ============================================

export function useSyntheticDataHealth() {
  return useQuery<{ status: string }, Error>({
    queryKey: ["synthetic-data-health"],
    queryFn: () => syntheticDataApi.healthCheckSynthetic(),
    refetchInterval: 30000,
  });
}

export function useGenerateSyntheticData() {
  return useMutation<SyntheticDataResponse, Error, SyntheticDataRequest>({
    mutationFn: async (data) => {
      return syntheticDataApi.generateSyntheticData(data);
    },
  });
}

// ============================================
// ORCHESTRATOR HOOKS (LOAN APPLICATION FLOW)
// ============================================

export function useSubmitApplicationMutation() {
  const queryClient = useQueryClient();

  return useMutation<LoanApplicationResponse, Error, LoanApplicationRequest>({
    mutationFn: async (request) => {
      return orchestratorApi.submitApplication(request);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      return data;
    },
  });
}

export function useApplicationQuery(applicationId: string | null) {
  return useQuery<LoanApplicationResponse, Error>({
    queryKey: ["applications", applicationId],
    queryFn: () => {
      if (!applicationId) throw new Error("No application ID");
      return orchestratorApi.getApplication(applicationId);
    },
    refetchInterval: applicationId ? 1000 : false,
    enabled: !!applicationId,
  });
}

export function usePollApplicationMutation() {
  return useMutation<LoanApplicationResponse, Error, {
    appId: string;
    onUpdate?: (app: LoanApplicationResponse) => void;
    maxAttempts?: number;
    intervalMs?: number;
  }>({
    mutationFn: async ({ appId, onUpdate, maxAttempts, intervalMs }) => {
      return orchestratorApi.pollApplication(appId, onUpdate, maxAttempts, intervalMs);
    },
  });
}

// ============================================
// POLICY HOOKS
// ============================================

export function usePolicyEvaluateMutation() {
  return useMutation<PolicyDecisionResult, Error, PolicyDecisionRequest>({
    mutationFn: async (request) => {
      return policyApi.evaluate(request);
    },
  });
}

// ============================================
// DATA ENRICHMENT HOOKS
// ============================================

export function useEnrichApplicantMutation() {
  return useMutation<EnrichmentResult, Error, ClientData>({
    mutationFn: async (data) => {
      return enrichmentApi.enrich(data);
    },
  });
}

// ============================================
// REPORT GENERATOR HOOKS
// ============================================

export function useGenerateReportMutation() {
  const queryClient = useQueryClient();

  return useMutation<ReportResponse, Error, ReportRequest>({
    mutationFn: async (request) => {
      return reportApi.generate(request);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["reports", data.report_id] });
    },
  });
}

export function useReportQuery(reportId: string | null) {
  return useQuery<ReportStatus, Error>({
    queryKey: ["reports", reportId],
    queryFn: () => {
      if (!reportId) throw new Error("No report ID");
      return reportApi.getReport(reportId);
    },
    refetchInterval: reportId ? 1000 : false,
    enabled: !!reportId,
  });
}

export function usePollReportMutation() {
  return useMutation<ReportStatus, Error, {
    reportId: string;
    onUpdate?: (status: ReportStatus) => void;
    maxAttempts?: number;
    intervalMs?: number;
  }>({
    mutationFn: async ({ reportId, onUpdate, maxAttempts, intervalMs }) => {
      return reportApi.pollReport(reportId, onUpdate, maxAttempts, intervalMs);
    },
  });
}

// ============================================
// COMPOSITE WORKFLOWS
// ============================================

/**
 * Complete loan application workflow with polling
 * Usage: Call this mutation with the initial request
 */
export function useCompleteApplicationWorkflow() {
  const submitMutation = useSubmitApplicationMutation();
  const pollMutation = usePollApplicationMutation();

  return useMutation<LoanApplicationResponse, Error, {
    request: LoanApplicationRequest;
    onStatusUpdate?: (app: LoanApplicationResponse) => void;
  }>({
    mutationFn: async ({ request, onStatusUpdate }) => {
      const { application_id } = await submitMutation.mutateAsync(request);
      return pollMutation.mutateAsync({
        appId: application_id,
        onUpdate: onStatusUpdate,
      });
    },
  });
}

/**
 * Full credit analysis workflow with enrichment, scoring, fraud, and policy
 */
export function useFullAnalysisMutation() {
  return useMutation<{
    prediction?: PredictionResult;
    similarApplicants?: SimilarApplicantsResult;
    fraudSimilar?: FraudSimilarResult;
    policy?: PolicyDecisionResult;
  }, Error, ApplicantData & Partial<ClientData>>({
    mutationFn: async (data) => {
      const results: {
        prediction?: PredictionResult;
        similarApplicants?: SimilarApplicantsResult;
        fraudSimilar?: FraudSimilarResult;
        policy?: PolicyDecisionResult;
      } = {};

      const [prediction, fraudSimilar] = await Promise.all([
        api.predict(data as ApplicantData),
        api.findSimilarFraud(data as ApplicantData, 10).catch(() => undefined),
      ]);
      results.prediction = prediction;
      results.fraudSimilar = fraudSimilar;

      if (prediction) {
        const policy = await policyApi
          .evaluate({
            risk_score: prediction.default_probability,
            requested_amount: 50000,
          })
          .catch(() => undefined);
        results.policy = policy;
      }

      return results;
    },
  });
}

// ============================================
// AGENTIC CREDIT SCORING HOOKS (CreditXAI)
// ============================================

export function useAgenticAnalysisMutation() {
  return useMutation<AgenticAnalysisResult, Error, {
    applicantId: string;
    features: ApplicantData;
    includeHistory?: boolean;
  }>({
    mutationFn: async ({ applicantId, features, includeHistory = true }) => {
      return augmentedScoringApi.getAgenticAnalysis(applicantId, features, includeHistory);
    },
  });
}

export function useAgenticReport(
  applicantId: string | null,
  features: ApplicantData | null,
  analysis: AgenticAnalysisResult | null,
) {
  return useQuery<AgenticReportResult, Error>({
    queryKey: ["agentic-report", applicantId, JSON.stringify(features)],
    queryFn: () => {
      if (!applicantId || !features || !analysis) throw new Error("Missing applicant ID or features");
      return augmentedScoringApi.getAgentReport(applicantId, features, analysis);
    },
    enabled: !!applicantId && !!features && !!analysis,
  });
}

/**
 * Complete agentic workflow with analysis and report generation
 */
export function useCompleteAgenticWorkflow() {
  const analysisMutation = useAgenticAnalysisMutation();
  const queryClient = useQueryClient();

  return useMutation<AgenticAnalysisResult, Error, {
    applicantId: string;
    features: ApplicantData;
  }>({
    mutationFn: async ({ applicantId, features }) => {
      const analysis = await analysisMutation.mutateAsync({
        applicantId,
        features,
        includeHistory: true,
      });

      queryClient.prefetchQuery({
        queryKey: ["agentic-report", applicantId, JSON.stringify(features)],
        queryFn: () => augmentedScoringApi.getAgentReport(applicantId, features, analysis),
      });

      return analysis;
    },
  });
}
