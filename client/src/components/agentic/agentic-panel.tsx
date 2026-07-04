"use client";

import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Bot, FileText } from "lucide-react";
import {
  ApplicantData,
  AgenticAnalysisResult,
  AgenticReportResult,
  BehavioralRiskAgent,
  FinancialRiskAgent,
  GovernanceRiskAgent,
  CompositeRiskAgent,
  ConsensusArbitrationAgent,
  SafetySupervisionAgent,
} from "@/lib/types";
import { ShimmerTiltCard, ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { Tabs } from "@/components/ui/tabs";
import { useAgenticAnalysisMutation, useAgenticReport } from "@/hooks/use-credit-api";
import styles from "./agentic-panel.module.scss";

interface AgenticPanelProps {
  applicantId: string;
  features: ApplicantData | null;
}

export function AgenticPanel({ applicantId, features }: AgenticPanelProps) {
  const [analysis, setAnalysis] = useState<AgenticAnalysisResult | null>(null);
  const [activeAgentKey, setActiveAgentKey] = useState<string>("bra");
  const [showReport, setShowReport] = useState(false);

  const { mutate: analyze, isPending: isAnalyzing } = useAgenticAnalysisMutation();
  const { data: report, isLoading: isReportLoading } = useAgenticReport(
    showReport ? applicantId : null,
    showReport ? features : null,
    showReport ? analysis : null
  );

  // Auto-analyze on features change
  useEffect(() => {
    if (!features) return;

    const timeoutId = setTimeout(() => {
      analyze(
        { applicantId, features, includeHistory: true },
        {
          onSuccess: (data) => {
            setAnalysis(data);
          },
        }
      );
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [applicantId, features, analyze]);

  // Helper: get risk color class from risk score
  function getRiskColorClass(risk: number | string): string {
    const num = typeof risk === "string" ? parseFloat(risk) : risk;
    if (isNaN(num)) return styles.riskColorNeutral;
    if (num >= 0.7) return styles.riskColorRed;
    if (num >= 0.4) return styles.riskColorYellow;
    return styles.riskColorGreen;
  }

  // Helper: get risk bg class from risk score
  function getRiskBgClass(risk: number | string): string {
    const num = typeof risk === "string" ? parseFloat(risk) : risk;
    if (isNaN(num)) return styles.riskBgNeutral;
    if (num >= 0.7) return styles.riskBgRed;
    if (num >= 0.4) return styles.riskBgYellow;
    return styles.riskBgGreen;
  }

  // Helper: get risk level badge class
  function getRiskLevelBadgeClass(level: string): string {
    if (level === "high") return styles.riskLevelBadgeHigh;
    if (level === "medium") return styles.riskLevelBadgeMedium;
    return styles.riskLevelBadgeLow;
  }

  // Normalize agent scores to 0-1 for display
  // BRA/FRA now return genuine 0-1 risk scores (not weighted fractions),
  // so no de-weighting is needed — just clamp to [0, 1].
  function normalizeAgentScore(agent: any): number {
    if ("risk_score" in agent && typeof agent.risk_score === "number") {
      return Math.min(1, Math.max(0, agent.risk_score));
    }
    if ("composite_score" in agent && typeof agent.composite_score === "number") return agent.composite_score;
    if ("confidence" in agent && typeof agent.confidence === "number") return agent.confidence;
    // Governance Risk Agent exposes no single risk_score; derive a 0-1 risk
    // from fraud_risk (max 0.3) and reputational_risk (max 0.2), matching the
    // normalized display in the Governance Metrics sub-section below.
    if ("fraud_risk" in agent && "reputational_risk" in agent) {
      const fraud = Math.min(1, (agent.fraud_risk ?? 0) / 0.3);
      const reputational = Math.min(1, (agent.reputational_risk ?? 0) / 0.2);
      return Math.min(1, Math.max(0, (fraud + reputational) / 2));
    }
    return 0;
  }

  // Format a 0-1 value as percentage
  function formatPct(value: number): string {
    return (value * 100).toFixed(0) + "%";
  }

  if (isAnalyzing) {
    return (
      <div className={styles.loadingState}>
        <div className={styles.loadingInner}>
          <svg className={styles.loadingSpinner} viewBox="0 0 24 24">
            <circle className={styles.spinnerCircle} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className={styles.spinnerPath} fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span className={styles.loadingText}>Running multi-agent analysis...</span>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className={styles.emptyState}>
        <div className={styles.emptyInner}>
          <Bot className={styles.emptyIcon} size={24} />
          <p className={styles.emptyText}>Enter applicant data to run agentic analysis</p>
        </div>
      </div>
    );
  }

  // Build agent entries from the actual type structure
  const agentEntries: { key: string; label: string; data: BehavioralRiskAgent | FinancialRiskAgent | GovernanceRiskAgent | CompositeRiskAgent }[] = [
    { key: "bra", label: "Behavioral Risk", data: analysis.agents.bra },
    { key: "fra", label: "Financial Risk", data: analysis.agents.fra },
    { key: "gra", label: "Governance Risk", data: analysis.agents.gra },
    { key: "cra", label: "Composite Risk", data: analysis.agents.cra },
  ];

  const agentTabs = agentEntries.map((a) => ({
    title: a.label,
    value: a.key,
  }));

  const activeEntry = agentEntries.find((a) => a.key === activeAgentKey) || agentEntries[0];
  const activeData = activeEntry.data;

  return (
    <div className={styles.panel}>
      {/* Header with combined score */}
      <div className={styles.header}>
        <div>
          <h2 className={styles.headerTitle}>
            <Bot className={styles.headerIcon} size={22} />
            Multi-Agent Analysis
          </h2>
          <p className={styles.headerSubtitle}>{agentEntries.length} agents analyzed</p>
        </div>
        <div className={cn(styles.riskBadgeContainer, getRiskBgClass(analysis.combined_risk_score))}>
          <span className={cn(styles.riskBadgeText, getRiskColorClass(analysis.combined_risk_score))}>
            Combined: {(analysis.combined_risk_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Consensus / Recommendation */}
      <ShimmerBorder borderRadius="1rem">
        <div>
          <div className={styles.consensusGrid}>
            <div>
              <p className={styles.sectionLabel}>Recommendation</p>
              <p className={styles.sectionValue}>{analysis.recommendation}</p>
            </div>
            <div>
              <p className={styles.sectionLabel}>Confidence</p>
              <p className={styles.sectionValuePrimary}>{(analysis.confidence * 100).toFixed(0)}%</p>
            </div>
          </div>
          {analysis.caa && (
            <div className={styles.consensusDivider}>
              <p className={styles.consensusLabel}>Consensus Decision</p>
              <p className={styles.consensusDecision}>{analysis.caa.consensus_decision}</p>
              {analysis.caa.rationale && (
                <p className={styles.consensusRationale}>{analysis.caa.rationale}</p>
              )}
            </div>
          )}
        </div>
      </ShimmerBorder>

      {/* Agent Tabs */}
      <Tabs
        tabs={agentTabs}
        activeTab={activeAgentKey}
        onChange={setActiveAgentKey}
      />

      {/* Active Agent Detail */}
      <ShimmerTiltCard>
        <div className={styles.agentDetail}>
          <div className={styles.agentDetailHeader}>
            <div>
              <h3 className={styles.agentDetailTitle}>{activeEntry.label}</h3>
              <p className={styles.agentDetailId}>{activeData.agent}</p>
            </div>
            <div className={cn(styles.agentScoreBadge, getRiskBgClass(normalizeAgentScore(activeData)))}>
              <span className={cn(styles.agentScoreText, getRiskColorClass(normalizeAgentScore(activeData)))}>
                {formatPct(normalizeAgentScore(activeData))}
              </span>
            </div>
          </div>

          {/* Agent-specific details */}
          {"analysis" in activeData && activeData.analysis && (
            <div className={styles.agentSubSection}>
              <h4 className={styles.agentSubLabel}>Analysis</h4>
              <p className={styles.agentSubText}>{(activeData as BehavioralRiskAgent).analysis}</p>
            </div>
          )}

          {"financial_health" in activeData && (activeData as FinancialRiskAgent).financial_health && (
            <div className={styles.agentSubSection}>
              <h4 className={styles.agentSubLabel}>Financial Health</h4>
              <p className={styles.agentSubText}>{(activeData as FinancialRiskAgent).financial_health}</p>
              {(activeData as FinancialRiskAgent).key_metrics && (
                <div className={styles.keyMetricsGrid}>
                  {Object.entries((activeData as FinancialRiskAgent).key_metrics).map(([key, value]) => (
                    <div key={key} className={styles.keyMetricItem}>
                      <span className={styles.keyMetricKey}>{key.replace(/_/g, " ")}</span>
                      <span className={styles.keyMetricValue}>{String(value)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {"trust_score" in activeData && (
            <div className={styles.agentSubSection}>
              <h4 className={styles.agentSubLabel}>Governance Metrics</h4>
              <div className={styles.governanceGrid}>
                <div className={styles.governanceItem}>
                  <p className={styles.governanceLabel}>Trust</p>
                  <p className={styles.governanceValue}>{formatPct((activeData as GovernanceRiskAgent).trust_score)}</p>
                </div>
                <div className={styles.governanceItem}>
                  <p className={styles.governanceLabel}>Fraud Risk</p>
                  <p className={styles.governanceValueRed}>{formatPct(Math.min(1, ((activeData as GovernanceRiskAgent).fraud_risk) / 0.3))}</p>
                </div>
                <div className={styles.governanceItem}>
                  <p className={styles.governanceLabel}>Reputational</p>
                  <p className={styles.governanceValueYellow}>{formatPct(Math.min(1, ((activeData as GovernanceRiskAgent).reputational_risk) / 0.2))}</p>
                </div>
              </div>
            </div>
          )}

          {"rating" in activeData && (activeData as CompositeRiskAgent).rating && (
            <div className={styles.agentSubSection}>
              <h4 className={styles.agentSubLabel}>Composite Rating</h4>
              <div className={styles.compositeRating}>
                <span className={cn(styles.compositeRatingValue, getRiskColorClass((activeData as CompositeRiskAgent).composite_score))}>
                  {(activeData as CompositeRiskAgent).rating}
                </span>
                <span className={styles.compositeRatingMethod}>
                  via {(activeData as CompositeRiskAgent).method}
                </span>
              </div>
            </div>
          )}

          {/* Risk Level */}
          {activeData.risk_level && (
            <div className={styles.riskLevelRow}>
              <span className={styles.riskLevelLabel}>Risk Level:</span>
              <span className={cn(styles.riskLevelBadge, getRiskLevelBadgeClass(activeData.risk_level))}>
                {activeData.risk_level}
              </span>
            </div>
          )}
        </div>
      </ShimmerTiltCard>

      {/* Agent Grid Overview */}
      <div className={styles.agentGrid}>
        {agentEntries.map((entry) => {
          const score = normalizeAgentScore(entry.data);
          return (
            <button
              key={entry.key}
              onClick={() => setActiveAgentKey(entry.key)}
              className={cn(
                styles.agentGridButton,
                entry.key === activeAgentKey ? styles.agentGridButtonActive : styles.agentGridButtonInactive
              )}
            >
              <p className={styles.agentGridLabel}>{entry.label}</p>
              <p className={cn(styles.agentGridScore, getRiskColorClass(normalizeAgentScore(entry.data)))}>
                {formatPct(normalizeAgentScore(entry.data))}
              </p>
            </button>
          );
        })}
      </div>

      {/* Safety Supervision */}
      {analysis.ssa && (
        <ShimmerBorder borderRadius="1rem">
          <div>
            <h3 className={cn(styles.sectionLabel, styles.safetyLabel)}>
              Safety Supervision
            </h3>
            <div className={styles.safetyGrid}>
              <div className={styles.safetyItem}>
                <p className={styles.safetyLabel}>Validation</p>
                <p className={analysis.ssa.validation_passed ? styles.safetyValueGreen : styles.safetyValueRed}>
                  {analysis.ssa.validation_passed ? "Passed" : "Failed"}
                </p>
              </div>
              <div className={styles.safetyItem}>
                <p className={styles.safetyLabel}>Quality Score</p>
                <p className={styles.safetyValuePrimary}>{(analysis.ssa.quality_score * 100).toFixed(0)}%</p>
              </div>
            </div>
            {analysis.ssa.anomalies_detected && analysis.ssa.anomalies_detected.length > 0 && (
              <div className={styles.anomaliesSection}>
                <p className={styles.anomaliesLabel}>Anomalies</p>
                {analysis.ssa.anomalies_detected.map((anomaly, i) => (
                  <p key={i} className={styles.anomalyItem}>{anomaly}</p>
                ))}
              </div>
            )}
          </div>
        </ShimmerBorder>
      )}

      {/* Causal Insights */}
      {analysis.causal_insights && (
        <ShimmerBorder borderRadius="1rem">
          <div>
            <h3 className={cn(styles.sectionLabel, styles.causalInsightLabel)}>Causal Insights</h3>
            <div className={styles.causalInsightsList}>
              <div className={styles.causalInsightRow}>
                <span className={styles.causalInsightLabel}>Propensity Tier</span>
                <span className={styles.causalInsightValue}>{analysis.causal_insights.propensity_tier}</span>
              </div>
              <div className={styles.causalInsightRow}>
                <span className={styles.causalInsightLabel}>Optimal Decision</span>
                <span className={styles.causalInsightValue}>{analysis.causal_insights.optimal_decision}</span>
              </div>
              <div className={styles.causalInsightRow}>
                <span className={styles.causalInsightLabel}>Counterfactuals</span>
                <span className={styles.causalInsightValue}>{analysis.causal_insights.counterfactuals_count}</span>
              </div>
            </div>
          </div>
        </ShimmerBorder>
      )}

      {/* Report Button */}
      {!showReport && (
        <button
          onClick={() => setShowReport(true)}
          className={styles.reportButton}
        >
          Generate Full Report
        </button>
      )}

      {/* Report Display */}
      {showReport && report && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.reportContent}>
            <h3 className={styles.reportTitle}>
              <FileText className={styles.reportTitleIcon} size={20} />
              Agentic Report
            </h3>

            {report.executive_summary && (
              <div className={styles.execSummarySection}>
                <h4 className={styles.execSummaryLabel}>Executive Summary</h4>
                <div className={styles.execSummaryGrid}>
                  <div className={styles.execSummaryItem}>
                    <p className={styles.execSummaryItemLabel}>Rating</p>
                    <p className={styles.execSummaryItemValue}>{report.executive_summary.rating}</p>
                  </div>
                  <div className={styles.execSummaryItem}>
                    <p className={styles.execSummaryItemLabel}>Outlook</p>
                    <p className={styles.execSummaryItemValueSm}>{report.executive_summary.outlook}</p>
                  </div>
                  <div className={styles.execSummaryItem}>
                    <p className={styles.execSummaryItemLabel}>Recommendation</p>
                    <p className={styles.execSummaryItemValueSm}>{report.executive_summary.recommendation}</p>
                  </div>
                </div>
                {report.executive_summary.key_factors && report.executive_summary.key_factors.length > 0 && (
                  <div className={styles.keyFactorsSection}>
                    <p className={styles.keyFactorsLabel}>Key Factors</p>
                    {report.executive_summary.key_factors.map((factor: string, i: number) => (
                      <div key={i} className={styles.keyFactorItem}>
                        <span className={styles.keyFactorDot} />
                        <span>{factor}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {report.risk_assessment && (
              <div className={styles.riskAssessmentSection}>
                <h4 className={styles.sectionLabel}>Risk Assessment</h4>
                {Object.entries(report.risk_assessment).map(([key, value]) => (
                  <div key={key} className={styles.riskAssessmentRow}>
                    <span className={styles.riskAssessmentKey}>{key.replace(/_/g, " ")}</span>
                    <span className={styles.riskAssessmentValue}>{String(value)}</span>
                  </div>
                ))}
              </div>
            )}

            {report.agent_consensus && (
              <div className={styles.agentConsensusSection}>
                <h4 className={styles.sectionLabel}>Agent Consensus</h4>
                <div className={styles.agentConsensusGrid}>
                  {Object.entries(report.agent_consensus).map(([key, value]) => {
                    // Scores are already 0-1 risk scores (same values as the
                    // agent grid above). Display them directly — do NOT divide
                    // by agent weights, which produced inflated, contradictory
                    // values (e.g. fra 99% next to a 59% grid tile).
                    const display = typeof value === "number"
                      ? formatPct(Math.min(1, Math.max(0, value)))
                      : String(value);
                    return (
                      <div key={key} className={styles.agentConsensusItem}>
                        <p className={styles.agentConsensusItemLabel}>{key.replace(/_/g, " ")}</p>
                        <p className={styles.agentConsensusItemValue}>{display}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {report.methodology && (
              <div className={styles.methodologySection}>
                <h4 className={styles.methodologyLabel}>Methodology</h4>
                <p className={styles.methodologyText}>{report.methodology}</p>
              </div>
            )}

            {report.combined_risk_score !== undefined && (
              <div className={styles.combinedRiskBar}>
                <span className={styles.combinedRiskLabel}>Combined Risk Score</span>
                <span className={cn(styles.combinedRiskValue, getRiskColorClass(report.combined_risk_score))}>
                  {(report.combined_risk_score * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        </ShimmerBorder>
      )}

      {showReport && isReportLoading && (
        <div className={styles.reportLoadingInner}>
          <svg className={styles.reportLoadingSpinner} viewBox="0 0 24 24">
            <circle className={styles.spinnerCircle} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className={styles.spinnerPath} fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span className={styles.reportLoadingText}>Generating report...</span>
        </div>
      )}
    </div>
  );
}
