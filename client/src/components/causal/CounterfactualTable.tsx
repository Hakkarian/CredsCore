"use client";

import { cn } from "@/lib/utils";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { CounterfactualOutcome } from "@/lib/api";
import styles from "./CounterfactualTable.module.scss";

interface CounterfactualTableProps {
  outcomes: CounterfactualOutcome[];
}

function getImpactColorClass(impact: string): string {
  switch (impact) {
    case "increase":
      return styles.impactIncrease;
    case "decrease":
      return styles.impactDecrease;
    default:
      return styles.impactNeutral;
  }
}

function getImpactIcon(impact: string): string {
  switch (impact) {
    case "increase":
      return "\u25B2";
    case "decrease":
      return "\u25BC";
    default:
      return "\u25CF";
  }
}

export function CounterfactualTable({ outcomes }: CounterfactualTableProps) {
  if (!outcomes || outcomes.length === 0) {
    return (
      <div className={styles.emptyMessage}>
        No counterfactual scenarios available
      </div>
    );
  }

  return (
    <ShimmerBorder borderRadius="1rem">
      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr className={styles.tableHead}>
              <th className={styles.thLeft}>Scenario</th>
              <th className={styles.thRight}>Treatment</th>
              <th className={styles.thRight}>Outcome</th>
              <th className={styles.thRight}>Change</th>
              <th className={styles.thCenter}>Impact</th>
            </tr>
          </thead>
          <tbody>
            {outcomes.map((outcome, index) => (
              <tr key={index} className={styles.tableRow}>
                <td className={styles.tdScenario}>{outcome.scenario}</td>
                <td className={styles.tdRight}>
                  {outcome.treatment_value.toFixed(2)}
                </td>
                <td className={styles.tdRight}>
                  {outcome.expected_outcome.toFixed(2)}
                </td>
                <td className={styles.tdRight}>
                  {outcome.outcome_change.toFixed(2)}
                </td>
                <td className={styles.tdCenter}>
                  <span className={cn(styles.impactBadge, getImpactColorClass(outcome.risk_impact))}>
                    {getImpactIcon(outcome.risk_impact)} {outcome.risk_impact}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </ShimmerBorder>
  );
}
