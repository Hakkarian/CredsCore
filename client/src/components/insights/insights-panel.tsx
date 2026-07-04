"use client";

import { useState, useEffect } from "react";
import { BarChart3, Lightbulb, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { augmentedScoringApi, ApplicantData, InsightsResult } from "@/lib/api";
import type { CounterfactualInsight } from "@/lib/types";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./insights-panel.module.scss";

interface InsightsPanelProps {
  applicantId: string;
  features: ApplicantData | null;
}

export function InsightsPanel({ applicantId, features }: InsightsPanelProps) {
  const [insights, setInsights] = useState<InsightsResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-fetch on features change (with debounce)
  useEffect(() => {
    if (!features) return;

    const timeoutId = setTimeout(() => {
      async function fetchInsights() {
        if (!features) return;
        setLoading(true);
        setError(null);
        try {
          const data = await augmentedScoringApi.getInsights(applicantId, features);
          setInsights(data);
        } catch (err) {
          setError(err instanceof Error ? err.message : "Failed to fetch insights");
        } finally {
          setLoading(false);
        }
      }

      fetchInsights();
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [applicantId, features]);

  if (loading) {
    return (
      <div className={styles.loadingState}>
        <div className={styles.loadingInner}>
          <Loader2 className={styles.loadingSpinner} />
          <span className={styles.loadingText}>Analyzing causal and social factors...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorState}>
        <div className={styles.errorInner}>
          <p className={styles.errorMessage}>Error: {error}</p>
          <button
            onClick={() => window.location.reload()}
            className={styles.retryButton}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!insights) {
    return (
      <div className={styles.emptyState}>
        <div className={styles.emptyInner}>
          <span className={styles.emptyIcon}><BarChart3 className={styles.emptyIconSvg} /></span>
          <p className={styles.emptyText}>Enter applicant data to see insights</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.panel}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h2 className={styles.headerTitle}>
            <span className={styles.headerIcon}><Lightbulb className={styles.headerIconSvg} /></span>
            Analysis Insights
          </h2>
          <p className={styles.headerSubtitle}>Causal and social factor analysis</p>
        </div>
        <span className={cn(
          styles.riskBadge,
          insights.ml_risk_level === "high" ? styles.riskBadgeHigh :
          insights.ml_risk_level === "medium" ? styles.riskBadgeMedium :
          styles.riskBadgeLow
        )}>
          {insights.ml_risk_level} risk
        </span>
      </div>

      {/* ML + Combined Score */}
      <ShimmerBorder borderRadius="1rem">
        <div className={styles.mlSection}>
          <div>
            <p className={styles.mlLabel}>ML Risk Score</p>
            <p className={styles.mlScore}>
              {(insights.ml_risk * 100).toFixed(1)}%
            </p>
          </div>
          <div className={styles.mlMetrics}>
            <div className={styles.metricItem}>
              <p className={styles.metricLabel}>Propensity</p>
              <p className={styles.metricValue}>
                {(insights.propensity_score * 100).toFixed(0)}%
              </p>
            </div>
            <div className={styles.metricItem}>
              <p className={styles.metricLabel}>Social Trust</p>
              <p className={styles.metricValue}>
                {(insights.social_trust * 100).toFixed(0)}%
              </p>
            </div>
            <div className={styles.metricItem}>
              <p className={styles.metricLabel}>Fraud Risk</p>
              <p className={styles.metricValueFraud}>
                {(insights.fraud_risk * 100).toFixed(0)}%
              </p>
            </div>
          </div>
        </div>
      </ShimmerBorder>

      {/* Causal Analysis */}
      <ShimmerBorder borderRadius="1rem">
        <div className={styles.causalSection}>
          <h3 className={styles.sectionTitle}>Causal Analysis</h3>
          <div className={styles.causalGrid}>
            <div className={styles.causalItem}>
              <p className={styles.causalItemLabel}>Optimal Decision</p>
              <p className={styles.causalItemValue}>{insights.optimal_decision}</p>
            </div>
            <div className={styles.causalItem}>
              <p className={styles.causalItemLabel}>Causal Recommendation</p>
              <p className={styles.causalItemValuePrimary}>{insights.causal_recommendation}</p>
            </div>
            <div className={styles.causalItem}>
              <p className={styles.causalItemLabel}>Expected Improvement</p>
              <p className={cn(
                insights.expected_improvement > 0 ? styles.improvementPositive : styles.improvementNegative
              )}>
                {(insights.expected_improvement * 100).toFixed(1)}%
              </p>
            </div>
            <div className={styles.causalItem}>
              <p className={styles.causalItemLabel}>Confidence</p>
              <p className={styles.confidenceValue}>{(insights.confidence * 100).toFixed(0)}%</p>
            </div>
          </div>
        </div>
      </ShimmerBorder>

      {/* Social Capital */}
      <ShimmerBorder borderRadius="1rem">
        <div className={styles.socialSection}>
          <h3 className={styles.sectionTitle}>Social Capital</h3>
          <div className={styles.socialGrid}>
            <div className={styles.socialItem}>
              <p className={styles.socialLabel}>Social Credit</p>
              <p className={styles.socialValuePrimary}>{((insights.social_credit_score - 300) / 550 * 100).toFixed(0)}%</p>
            </div>
            <div className={styles.socialItem}>
              <p className={styles.socialLabel}>Influence</p>
              <p className={styles.socialValueDefault}>{(insights.social_influence * 100).toFixed(0)}%</p>
            </div>
            <div className={styles.socialItem}>
              <p className={styles.socialLabel}>Network Size</p>
              <p className={styles.socialValueDefault}>{insights.social_network_size}</p>
            </div>
            <div className={styles.socialItem}>
              <p className={styles.socialLabel}>Connections</p>
              <p className={styles.socialValueDefault}>{insights.social_connections}</p>
            </div>
          </div>
        </div>
      </ShimmerBorder>

      {/* Counterfactuals */}
      {insights.counterfactuals && insights.counterfactuals.length > 0 && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.counterfactualsSection}>
            <h3 className={styles.sectionTitle}>
              Counterfactual Scenarios
            </h3>
            <div className={styles.counterfactualsScroll}>
              <table className={styles.counterfactualsTable}>
                <thead>
                  <tr className={styles.tableHead}>
                    <th className={styles.thLeft}>Decision</th>
                    <th className={styles.thRight}>Probability</th>
                    <th className={styles.thRightLast}>Change</th>
                  </tr>
                </thead>
                <tbody>
                  {insights.counterfactuals.map((cf, i) => (
                    <tr key={i} className={styles.tableRow}>
                      <td className={styles.tdDecision}>{cf.decision}</td>
                      <td className={styles.tdProbability}>{(cf.probability * 100).toFixed(1)}%</td>
                      <td className={cn(
                        styles.tdChange,
                        cf.change > 0 ? styles.changePositive : styles.changeNegative
                      )}>
                        {cf.change > 0 ? "+" : ""}{(cf.change * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </ShimmerBorder>
      )}

      {/* Recommendation */}
      <ShimmerBorder borderRadius="1rem">
        <div className={styles.recommendationSection}>
          <h3 className={styles.recommendationTitle}>Recommendation</h3>
          <p className={styles.recommendationText}>{insights.recommendation}</p>
          {insights.summary && (
            <p className={styles.recommendationSummary}>{insights.summary}</p>
          )}
        </div>
      </ShimmerBorder>
    </div>
  );
}
