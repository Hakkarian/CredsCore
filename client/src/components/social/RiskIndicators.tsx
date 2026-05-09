"use client";

import { cn } from "@/lib/utils";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./RiskIndicators.module.scss";

interface RiskIndicatorsProps {
  indicators: {
    fraud_risk: number;
    default_risk: number;
    reputational_risk: number;
  };
}

interface RiskMetric {
  key: string;
  name: string;
  value: number;
  max: number;
  icon: string;
  description: string;
}

function getRiskLevel(normalized: number): "low" | "medium" | "high" {
  if (normalized < 0.33) return "low";
  if (normalized < 0.66) return "medium";
  return "high";
}

function getIconBoxClass(level: string): string {
  switch (level) {
    case "low": return styles.iconBoxLow;
    case "medium": return styles.iconBoxMedium;
    case "high": return styles.iconBoxHigh;
    default: return styles.iconBoxMedium;
  }
}

function getMetricValueClass(level: string): string {
  switch (level) {
    case "low": return styles.metricValueLow;
    case "medium": return styles.metricValueMedium;
    case "high": return styles.metricValueHigh;
    default: return styles.metricValueMedium;
  }
}

function getBarFillClass(level: string): string {
  switch (level) {
    case "low": return styles.barFillLow;
    case "medium": return styles.barFillMedium;
    case "high": return styles.barFillHigh;
    default: return styles.barFillMedium;
  }
}

export function RiskIndicators({ indicators }: RiskIndicatorsProps) {
  const metrics: RiskMetric[] = [
    {
      key: "fraud",
      name: "Fraud Risk",
      value: indicators.fraud_risk,
      max: 0.3,
      icon: "\u{1F6E1}\uFE0F",
      description: "Risk of fraudulent behavior based on network patterns",
    },
    {
      key: "default",
      name: "Default Risk",
      value: indicators.default_risk,
      max: 0.25,
      icon: "\u26A0\uFE0F",
      description: "Likelihood of default based on social connections",
    },
    {
      key: "reputational",
      name: "Reputational Risk",
      value: indicators.reputational_risk,
      max: 0.2,
      icon: "\u{1F4E1}",
      description: "Risk from association with high-risk entities",
    },
  ];

  return (
    <div className={styles.container}>
      <h3 className={styles.sectionTitle}>Risk Indicators</h3>
      {metrics.map((metric) => {
        const normalized = Math.min(1, metric.value / metric.max);
        const level = getRiskLevel(normalized);
        return (
          <ShimmerBorder key={metric.key} borderRadius="0.75rem">
            <div className={styles.metricRow}>
              <div className={cn(styles.iconBox, getIconBoxClass(level))}>
                {metric.icon}
              </div>
              <div className={styles.metricInfo}>
                <div className={styles.metricHeader}>
                  <span className={styles.metricName}>{metric.name}</span>
                  <span className={cn(styles.metricValue, getMetricValueClass(level))}>
                    {(normalized * 100).toFixed(0)}%
                  </span>
                </div>
                <div className={styles.barTrack}>
                  <div
                    className={cn(styles.barFill, getBarFillClass(level))}
                    style={{ width: `${normalized * 100}%` }}
                  />
                </div>
                <p className={styles.metricDescription}>{metric.description}</p>
              </div>
            </div>
          </ShimmerBorder>
        );
      })}
    </div>
  );
}
