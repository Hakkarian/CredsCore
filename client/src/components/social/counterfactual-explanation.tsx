"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./counterfactual-explanation.module.scss";

interface CounterfactualScenario {
  scenario: string;
  treatment_value: number;
  expected_outcome: number;
  outcome_change: number;
  risk_impact: "increase" | "decrease" | "neutral";
}

interface CounterfactualPanelProps {
  scenarios: CounterfactualScenario[];
}

export function CounterfactualPanel({ scenarios }: CounterfactualPanelProps) {
  const [selectedScenario, setSelectedScenario] = useState<number | null>(null);

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <h3 className={styles.title}>Counterfactual Analysis</h3>
        <p className={styles.subtitle}>Explore &quot;what-if&quot; scenarios for credit decisions</p>
      </div>

      {/* Scenarios List */}
      <div className={styles.scenariosList}>
        {scenarios.map((scenario, index) => (
          <button
            key={index}
            onClick={() => setSelectedScenario(index)}
            className={cn(
              styles.scenarioButton,
              selectedScenario === index && styles.scenarioButtonSelected
            )}
          >
            <div className={styles.scenarioRow}>
              <span className={styles.scenarioName}>{scenario.scenario}</span>
              <span className={cn(
                styles.scenarioChange,
                scenario.risk_impact === "increase" ? styles.scenarioChangeIncrease :
                scenario.risk_impact === "decrease" ? styles.scenarioChangeDecrease :
                styles.scenarioChangeNeutral
              )}>
                {scenario.risk_impact === "increase" ? "\u2191" : scenario.risk_impact === "decrease" ? "\u2193" : "\u2192"}
                {scenario.outcome_change > 0 ? "+" : ""}{(scenario.outcome_change * 100).toFixed(1)}%
              </span>
            </div>

            {selectedScenario === index && (
              <div className={styles.scenarioDetails}>
                <div>
                  <p className={styles.detailLabel}>Treatment</p>
                  <p className={styles.detailValue}>{scenario.treatment_value}</p>
                </div>
                <div>
                  <p className={styles.detailLabel}>Expected</p>
                  <p className={styles.detailValue}>{(scenario.expected_outcome * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className={styles.detailLabel}>Impact</p>
                  <p className={cn(
                    styles.detailValue,
                    scenario.risk_impact === "increase" ? styles.detailValueIncrease :
                    scenario.risk_impact === "decrease" ? styles.detailValueDecrease :
                    styles.detailValueNeutral
                  )}>
                    {scenario.risk_impact}
                  </p>
                </div>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
