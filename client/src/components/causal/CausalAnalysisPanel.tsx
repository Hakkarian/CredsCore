"use client";

import { useState, useEffect } from "react";
import { Microscope, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { api, CausalAnalysisResult, TreatmentEffect } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { PropensityScoreChart } from "./PropensityScoreChart";
import { CounterfactualTable } from "./CounterfactualTable";
import styles from "./CausalAnalysisPanel.module.scss";

interface CausalAnalysisPanelProps {
  applicantId: string;
}

export function CausalAnalysisPanel({ applicantId }: CausalAnalysisPanelProps) {
  const [analysis, setAnalysis] = useState<CausalAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!applicantId) return;

    async function fetchAnalysis() {
      setLoading(true);
      setError(null);
      try {
        const result = await api.getCausalAnalysis(applicantId);
        setAnalysis(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load analysis");
      } finally {
        setLoading(false);
      }
    }

    fetchAnalysis();
  }, [applicantId]);

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingInner}>
          <Loader2 className={styles.spinner} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div className={styles.errorInner}>
          <p className={styles.errorText}>{error}</p>
          <button
            onClick={() => {
              setError(null);
              setAnalysis(null);
            }}
            className={styles.retryButton}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className={styles.emptyContainer}>
        <div className={styles.emptyInner}>
          <span className={styles.emptyIcon}><Microscope className={styles.emptyIconSvg} /></span>
          <p className={styles.emptyText}>No causal analysis available</p>
        </div>
      </div>
    );
  }

  const treatmentEffect: TreatmentEffect = analysis.treatment_effect;
  const counterfactualOutcomes = analysis.counterfactuals;

  return (
    <div className={styles.content}>
      {/* Header */}
      <div className={styles.header}>
        <h2 className={styles.title}>
          <span className={styles.titleIcon}><Microscope className={styles.titleIconSvg} /></span>
          Causal Analysis
        </h2>
        <p className={styles.subtitle}>What-if analysis and treatment effects</p>
      </div>

      {/* Key Metrics */}
      <ShimmerBorder borderRadius="1rem">
        <div className={styles.metricsGrid}>
          <div className={styles.metricCenter}>
            <p className={styles.metricLabel}>ATE</p>
            <p className={cn(
              treatmentEffect.estimate > 0 ? styles.metricValuePositive : styles.metricValueNegative
            )}>
              {treatmentEffect.estimate.toFixed(3)}
            </p>
          </div>
          <div className={styles.metricCenter}>
            <p className={styles.metricLabel}>P-Value</p>
            <p className={styles.metricValue}>{treatmentEffect.p_value.toFixed(3)}</p>
          </div>
          <div className={styles.metricCenter}>
            <p className={styles.metricLabel}>Scenarios</p>
            <p className={styles.metricValue}>{counterfactualOutcomes.length}</p>
          </div>
          <div className={styles.metricCenter}>
            <p className={styles.metricLabel}>95% CI</p>
            <p className={styles.metricValueSmall}>
              [{treatmentEffect.confidence_interval[0].toFixed(3)}, {treatmentEffect.confidence_interval[1].toFixed(3)}]
            </p>
          </div>
        </div>
      </ShimmerBorder>

      {/* Treatment Method & Significance */}
      <ShimmerBorder borderRadius="1rem">
        <div className={styles.methodGrid}>
          <div>
            <p className={styles.methodLabel}>Method</p>
            <p className={styles.methodValue}>
              {treatmentEffect.method.replace(/_/g, " ")}
            </p>
          </div>
          <div>
            <p className={styles.methodLabel}>Significance</p>
            <p className={cn(
              treatmentEffect.significance === "significant" ? styles.methodValueSignificant : styles.methodValueNotSignificant
            )}>
              {treatmentEffect.significance.replace(/_/g, " ")}
            </p>
          </div>
          <div>
            <p className={styles.methodLabel}>Std Error</p>
            <p className={styles.methodValue}>{treatmentEffect.standard_error.toFixed(4)}</p>
          </div>
        </div>
      </ShimmerBorder>

      {/* Interpretation */}
      {analysis.interpretation && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.interpretationContent}>
            <h3 className={styles.interpretationTitle}>Interpretation</h3>
            <div className={styles.interpretationList}>
              <div className={styles.interpretationRow}>
                <span className={styles.interpretationLabel}>Causal Impact</span>
                <span className={styles.interpretationValue}>{analysis.interpretation.causal_impact}</span>
              </div>
              <div className={styles.interpretationRow}>
                <span className={styles.interpretationLabel}>Recommendation</span>
                <span className={styles.interpretationValue}>{analysis.interpretation.recommendation}</span>
              </div>
              <div className={styles.interpretationRow}>
                <span className={styles.interpretationLabel}>Confidence Level</span>
                <span className={styles.interpretationValuePrimary}>{analysis.interpretation.confidence_level}</span>
              </div>
            </div>
          </div>
        </ShimmerBorder>
      )}

      {/* Propensity Score Chart */}
      {analysis.propensity_scores && analysis.propensity_scores.length > 0 && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.propensitySection}>
            <h3 className={styles.propensityTitle}>
              Propensity Score Distribution
            </h3>
            <PropensityScoreChart data={analysis.propensity_scores} />
          </div>
        </ShimmerBorder>
      )}

      {/* Covariate Balance */}
      {analysis.covariate_balance && Object.keys(analysis.covariate_balance).length > 0 && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.covariateSection}>
            <h3 className={styles.covariateTitle}>
              Covariate Balance
            </h3>
            <div className={styles.covariateList}>
              {Object.entries(analysis.covariate_balance).map(([feature, balance]) => (
                <div key={feature} className={styles.covariateRow}>
                  <span className={styles.covariateName}>{feature}</span>
                  <div className={styles.covariateDetails}>
                    <span className={styles.covariateBefore}>Before: {balance.before.toFixed(3)}</span>
                    <span className={styles.covariateAfter}>After: {balance.after.toFixed(3)}</span>
                    <span className={cn(
                      Math.abs(balance.after) < Math.abs(balance.before) ? styles.covariateImproved : styles.covariateUnchanged
                    )}>
                      {balance.after < balance.before ? "Improved" : "Unchanged"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </ShimmerBorder>
      )}

      {/* Counterfactual Table */}
      {counterfactualOutcomes.length > 0 && (
        <ShimmerBorder borderRadius="1rem">
          <div className={styles.counterfactualSection}>
            <h3 className={styles.counterfactualTitle}>
              Counterfactual Scenarios
            </h3>
            <CounterfactualTable outcomes={counterfactualOutcomes} />
          </div>
        </ShimmerBorder>
      )}
    </div>
  );
}
