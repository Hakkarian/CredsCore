"use client";

import { cn } from "@/lib/utils";
import { QualityMetrics as QualityMetricsType } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./quality-metrics.module.scss";

interface QualityMetricsDisplayProps {
  metrics: QualityMetricsType;
}

function getQualityLevel(value: number): "low" | "medium" | "high" {
  if (value >= 0.8) return "high";
  if (value >= 0.5) return "medium";
  return "low";
}

function getQualityColorClass(level: string): string {
  switch (level) {
    case "high":
      return styles.qualityHigh;
    case "medium":
      return styles.qualityMedium;
    case "low":
      return styles.qualityLow;
    default:
      return styles.qualityDefault;
  }
}

function getBarColorClass(level: string): string {
  switch (level) {
    case "high":
      return styles.barHigh;
    case "medium":
      return styles.barMedium;
    case "low":
      return styles.barLow;
    default:
      return styles.barDefault;
  }
}

export function QualityMetricsDisplay({ metrics }: QualityMetricsDisplayProps) {
  const metricEntries: { key: string; label: string; value: number }[] = [
    { key: "similarity_score", label: "Similarity Score", value: metrics.similarity_score },
    { key: "privacy_score", label: "Privacy Score", value: metrics.privacy_score },
    { key: "validity_score", label: "Validity Score", value: metrics.validity_score },
    { key: "overall_score", label: "Overall Score", value: metrics.overall_score },
  ];

  return (
    <ShimmerBorder borderRadius="1rem">
      <div className={styles.container}>
        <h3 className={styles.title}>Quality Metrics</h3>

        <div className={styles.metricsGrid}>
          {metricEntries.map((metric) => {
            const level = getQualityLevel(metric.value);
            return (
              <div key={metric.key} className={styles.metricItem}>
                <div className={styles.metricHeader}>
                  <span className={styles.metricLabel}>{metric.label}</span>
                  <span className={cn(styles.metricValue, getQualityColorClass(level))}>
                    {(metric.value * 100).toFixed(1)}%
                  </span>
                </div>
                <div className={styles.progressBar}>
                  <div
                    className={cn(getBarColorClass(level))}
                    style={{ width: `${metric.value * 100}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </ShimmerBorder>
  );
}
