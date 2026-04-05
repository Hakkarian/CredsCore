"use client";

import cn from "classnames";
import { PredictionResult } from "@/lib/api";
import { STATS, RECENT_PREDICTIONS } from "./dashboard-header";
import { ProbabilityChart, RiskFactorsChart } from "./charts";
import styles from "./dashboard.module.scss";

interface PredictionResultsProps {
  result: PredictionResult | null;
}

export function PredictionResults({ result }: PredictionResultsProps) {
  if (!result) return null;

  return (
    <div className={styles.resultCard}>
      <div className={styles.resultHeader}>
        <div className={styles.resultHeaderLeft}>
          <h2 className={styles.resultTitle}>Prediction Result</h2>
          <p className={styles.resultMessage}>{result.message}</p>
        </div>
        <div
          className={cn(
            result.risk_level === "low" && styles.riskBadgeLow,
            result.risk_level === "medium" && styles.riskBadgeMedium,
            result.risk_level === "high" && styles.riskBadgeHigh
          )}
        >
          {result.risk_level.toUpperCase()} RISK
        </div>
      </div>

      <ProbabilityChart
        probability={result.default_probability}
        prediction={result.prediction}
      />

      <RiskFactorsChart factors={result.top_risk_factors} />
    </div>
  );
}

export function StatsGrid() {
  return (
    <div className={styles.statsGrid}>
      {STATS.map((stat, i) => (
        <div key={i} className={styles.statCard}>
          <div className={styles.statHeader}>
            <span className={styles.statIcon}>{stat.icon}</span>
            <span
              className={cn(
                stat.trend.startsWith("+") ? styles.statTrendPositive : styles.statTrendNegative
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
  return (
    <div className={styles.tableCard}>
      <h3 className={styles.tableTitle}>Recent Predictions</h3>
      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr className={styles.tableHead}>
              <th className={styles.tableHeader}>ID</th>
              <th className={styles.tableHeader}>Probability</th>
              <th className={styles.tableHeader}>Risk Level</th>
              <th className={styles.tableHeader}>Time</th>
              <th className={styles.tableHeader}>Status</th>
            </tr>
          </thead>
          <tbody className={styles.tableBody}>
            {RECENT_PREDICTIONS.map((row, i) => (
              <tr key={i}>
                <td className={styles.tableCellId}>{row.id}</td>
                <td className={styles.tableCellText}>{row.prob}</td>
                <td className={styles.tableCellRisk}>
                  <span className={cn(
                    row.risk === "Low" && styles.riskTagLow,
                    row.risk === "Medium" && styles.riskTagMedium,
                    row.risk === "High" && styles.riskTagHigh
                  )}>
                    {row.risk}
                  </span>
                </td>
                <td className={styles.tableCellText}>{row.time}</td>
                <td className={styles.tableCellStatus}>
                  <span className={cn(
                    row.status === "Approved" && styles.statusTagApproved,
                    row.status === "Denied" && styles.statusTagDenied,
                    row.status === "Review" && styles.statusTagReview
                  )}>
                    {row.status}
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