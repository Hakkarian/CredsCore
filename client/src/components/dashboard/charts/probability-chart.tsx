"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import cn from "classnames";
import styles from "./charts.module.scss";

interface ProbabilityChartProps {
  probability: number;
  prediction: number;
  className?: string;
}

const getRiskLevel = (prob: number): { label: string; color: string } => {
  if (prob < 0.3) return { label: "LOW", color: "#22c55e" };
  if (prob < 0.6) return { label: "MEDIUM", color: "#eab308" };
  return { label: "HIGH", color: "#ef4444" };
};

export function ProbabilityChart({ probability, prediction, className }: ProbabilityChartProps) {
  const risk = getRiskLevel(probability);
  const percentage = (probability * 100).toFixed(1);
  
  const data = [
    { name: "Default Risk", value: probability },
    { name: "Safe", value: 1 - probability },
  ];

  return (
    <div className={cn(styles.probabilityChart, className)}>
      <div className={styles.probabilityChartHeader}>
        <div className={styles.probabilityChartLeft}>
          <h3 className={styles.chartTitle}>Default Probability</h3>
          <p className={styles.chartSubtitle}>Risk assessment score</p>
        </div>
        <span
          className={styles.riskBadge}
          style={{ backgroundColor: `${risk.color}20`, color: risk.color }}
        >
          {risk.label}
        </span>
      </div>
      
      <div className={styles.probabilityContent}>
        <div className={styles.probabilityChartContainer}>
          <ResponsiveContainer width="100%" height={112}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={24}
                outerRadius={36}
                startAngle={90}
                endAngle={-270}
                paddingAngle={2}
                dataKey="value"
                stroke="none"
              >
                {data.map((_, index) => (
                  <Cell key={index} fill={index === 0 ? risk.color : "rgba(255,255,255,0.08)"} />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload[0] && payload[0].value !== undefined) {
                    const val = payload[0].value as number;
                    return (
                      <div className={styles.tooltip}>
                        <span className={styles.tooltipName}>{payload[0].name}: </span>
                        <span className={styles.tooltipValue}>
                          {(val * 100).toFixed(1)}%
                        </span>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        <div>
          <div className={styles.probabilityValue}>{percentage}%</div>
          <div className={styles.probabilityLabel}>Probability of default</div>
          <div className={styles.probabilityAction} style={{ color: risk.color }}>
            {prediction === 0 ? "Approve" : "Deny"}
          </div>
        </div>
      </div>
    </div>
  );
}