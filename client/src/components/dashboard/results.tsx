"use client";

import { PredictionResult } from "@/lib/types";
import { STATS, RECENT_PREDICTIONS } from "./dashboard-header";
import { ProbabilityChart, RiskFactorsChart } from "./charts";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { cn } from "@/lib/utils";
import styles from "./results.module.scss";

interface PredictionResultsProps {
  result: PredictionResult | null;
}

export { PredictionResults as Results };

export function PredictionResults({ result }: PredictionResultsProps) {
  if (!result) return null;

  const riskBadgeStyles: Record<string, string> = {
    low: styles.riskLow,
    medium: styles.riskMedium,
    high: styles.riskHigh,
  };

  return (
    <ShimmerBorder className="rounded-2xl">
      <div>
        <div className={styles.resultHeader}>
          <div className={styles.resultHeaderLeft}>
            <h2 className={styles.resultTitle}>Prediction Result</h2>
            <p className={styles.resultMessage}>{result.message}</p>
          </div>
          <div className={cn(styles.riskBadge, riskBadgeStyles[result.risk_level])}>
            {result.risk_level.toUpperCase()} RISK
          </div>
        </div>

        <div className={styles.chartContainer}>
          <ProbabilityChart
            probability={result.default_probability}
            prediction={result.prediction}
          />
        </div>

        <div className={styles.chartContainerSpaced}>
          <RiskFactorsChart factors={result.top_risk_factors} />
        </div>
      </div>
    </ShimmerBorder>
  );
}

export function StatsGrid() {
  return (
    <div className={styles.statsGrid}>
      {STATS.map((stat, i) => (
        <div
          key={i}
          className={styles.statCard}
        >
          <div className={styles.statHeader}>
            <span className={styles.statIcon}>{stat.icon}</span>
            <span
              className={cn(
                styles.trendUp,
                !stat.trend.startsWith("+") && styles.trendDown
              )}
            >
              {stat.trend}
            </span>
          </div>
          <div className={styles.statValue}>{stat.value}</div>
          <div className={styles.statLabel}>{stat.label}</div>
        </div>
      ))}
    </div>
  );
}

export function RecentActivityTable() {
  const riskTagStyles: Record<string, string> = {
    low: styles.riskTagLow,
    medium: styles.riskTagMedium,
    high: styles.riskTagHigh,
  };

  const statusTagStyles: Record<string, string> = {
    approved: styles.statusApproved,
    denied: styles.statusDenied,
    review: styles.statusReview,
  };

  return (
    <div className={styles.activityCard}>
      <h3 className={styles.activityTitle}>Recent Activity</h3>
      <div className={styles.tableScroll}>
        <table className={styles.table}>
          <thead>
            <tr className={styles.tableHead}>
              <th className={styles.tableHeaderCell}>ID</th>
              <th className={styles.tableHeaderCell}>Name</th>
              <th className={styles.tableHeaderCell}>Risk</th>
              <th className={styles.tableHeaderCell}>Prob</th>
              <th className={styles.tableHeaderCell}>Status</th>
            </tr>
          </thead>
          <tbody>
            {RECENT_PREDICTIONS.map((p) => (
              <tr key={p.id} className={styles.tableRow}>
                <td className={styles.tableCellMedium}>{p.id}</td>
                <td className={styles.tableCellMuted}>{p.name}</td>
                <td className={styles.tableCell}>
                  <span className={cn(styles.riskTag, riskTagStyles[p.risk])}>
                    {p.risk}
                  </span>
                </td>
                <td className={styles.tableCellMuted}>{p.prob}</td>
                <td className={styles.tableCell}>
                  <span className={cn(styles.statusTag, statusTagStyles[p.status])}>
                    {p.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
