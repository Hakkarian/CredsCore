"use client";

import { cn } from "@/lib/utils";
import { DriftResult } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./drift-panel.module.scss";

interface DriftResultsViewProps {
  result: DriftResult;
}

function getDriftColorClass(level: string | undefined): string {
  if (!level) return styles.driftTextNeutral;
  const l = level.toLowerCase();
  if (l.includes("high")) return styles.driftTextHigh;
  if (l.includes("medium")) return styles.driftTextMedium;
  return styles.driftTextLow;
}

function getDriftBgClass(level: string | undefined): string {
  if (!level) return styles.driftBadgeDefault;
  const l = level.toLowerCase();
  if (l.includes("high")) return styles.driftBadgeHigh;
  if (l.includes("medium")) return styles.driftBadgeMedium;
  return styles.driftBadgeLow;
}

export function DriftResultsView({ result }: DriftResultsViewProps) {
  return (
    <ShimmerBorder borderRadius="1rem">
      <div className={styles.controlsSection}>
        <div className={styles.driftResultHeader}>
          <h3 className={styles.sectionTitle}>Drift Monitoring Results</h3>
          <div className={cn(styles.driftBadge, getDriftBgClass(result.drift_analysis.drift_level))}>
            <span className={cn(styles.driftBadgeText, getDriftColorClass(result.drift_analysis.drift_level))}>
              {result.drift_analysis.drift_level}
            </span>
          </div>
        </div>

        {/* Summary Stats from drift_analysis */}
        <div className={styles.driftSummaryGrid}>
          <div className={styles.driftSummaryCard}>
            <p className={styles.driftSummaryLabel}>KL Divergence</p>
            <p className={styles.driftSummaryValue}>
              {result.drift_analysis.kl_divergence.toFixed(3)}
            </p>
          </div>
          <div className={styles.driftSummaryCard}>
            <p className={styles.driftSummaryLabel}>Avg Distance</p>
            <p className={styles.driftSummaryValue}>
              {result.drift_analysis.avg_centroid_distance.toFixed(3)}
            </p>
          </div>
          <div className={styles.driftSummaryCard}>
            <p className={styles.driftSummaryLabel}>Max Distance</p>
            <p className={styles.driftSummaryValue}>
              {result.drift_analysis.max_centroid_distance.toFixed(3)}
            </p>
          </div>
          <div className={styles.driftSummaryCard}>
            <p className={styles.driftSummaryLabel}>Detected</p>
            <p className={cn(
              result.drift_analysis.drift_detected ? styles.driftSummaryValueRed : styles.driftSummaryValueGreen
            )}>
              {result.drift_analysis.drift_detected ? "Yes" : "No"}
            </p>
          </div>
        </div>

        {/* Interpretation */}
        {result.interpretation && (
          <div className={styles.interpretationSection}>
            <h4 className={styles.interpretationSectionTitle}>Interpretation</h4>
            <div className={styles.interpretationCard}>
              {result.interpretation.drift_detected !== undefined && (
                <div className={styles.interpretationRow}>
                  <span className={styles.interpretationLabel}>Drift Detected</span>
                  <span className={result.interpretation.drift_detected ? styles.interpretationValueRed : styles.interpretationValueGreen}>
                    {result.interpretation.drift_detected ? "Yes" : "No"}
                  </span>
                </div>
              )}
              {result.interpretation.drift_level && (
                <div className={styles.interpretationRow}>
                  <span className={styles.interpretationLabel}>Drift Level</span>
                  <span className={cn(
                    styles.interpretationValue,
                    getDriftColorClass(result.interpretation.drift_level)
                  )}>
                    {result.interpretation.drift_level}
                  </span>
                </div>
              )}
              {result.interpretation.kl_divergence && (
                <div className={styles.interpretationRow}>
                  <span className={styles.interpretationLabel}>KL Divergence</span>
                  <span className={styles.interpretationValue}>{result.interpretation.kl_divergence}</span>
                </div>
              )}
              {result.interpretation.avg_centroid_shift && (
                <div className={styles.interpretationRow}>
                  <span className={styles.interpretationLabel}>Avg Centroid Shift</span>
                  <span className={styles.interpretationValue}>{result.interpretation.avg_centroid_shift}</span>
                </div>
              )}
              {result.interpretation.recommendation && (
                <div className={styles.recommendation}>
                  <p className={styles.recommendationLabel}>Recommendation</p>
                  <p className={styles.recommendationText}>{result.interpretation.recommendation}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Human Explanation */}
        {result.human_explanation && (
          <div className={styles.explanationBox}>
            <p className={styles.explanationText}>{result.human_explanation}</p>
          </div>
        )}
      </div>
    </ShimmerBorder>
  );
}