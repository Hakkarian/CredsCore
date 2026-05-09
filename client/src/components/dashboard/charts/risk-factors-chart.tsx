"use client";

import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from "recharts";
import { cn } from "@/lib/utils";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { RiskFactor } from "@/lib/types";
import styles from "./risk-factors-chart.module.scss";

interface RiskFactorsChartProps {
  factors: RiskFactor[];
  className?: string;
}

export function RiskFactorsChart({ factors, className }: RiskFactorsChartProps) {
  const chartData = factors.map((f) => ({
    name: f.feature.replace(/([A-Z])/g, " $1").trim(),
    value: Math.abs(f.shap_value),
    impact: f.impact,
  }));

  const getBarColor = (impact: string) =>
    impact === "increases_risk" ? "#ef4444" : "#22c55e";

  return (
    <ShimmerBorder className={cn("rounded-2xl", className)}>
      <div>
        <div className={styles.header}>
          <h3 className={styles.title}>Top Risk Factors</h3>
          <p className={styles.subtitle}>SHAP feature importance</p>
        </div>

        <div className={styles.chartArea}>
          <ResponsiveContainer width="100%" height={224}>
            <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
              <XAxis
                type="number"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#9ca3af", fontSize: 11 }}
              />
              <YAxis
                type="category"
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#d1d5db", fontSize: 10 }}
                width={130}
              />
              <Bar dataKey="value" radius={[0, 3, 3, 0]} maxBarSize={16}>
                {chartData.map((entry, index) => (
                  <Cell key={index} fill={getBarColor(entry.impact)} />
                ))}
              </Bar>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload[0] && payload[0].payload) {
                    const item = payload[0].payload;
                    return (
                      <div className={styles.tooltip}>
                        <div className={styles.tooltipName}>{item.name}</div>
                        <div className={styles.tooltipValue}>
                          SHAP: {item.value.toFixed(4)}
                        </div>
                        <div className={cn(
                          styles.tooltipImpact,
                          item.impact === "increases_risk" ? styles.impactIncreases : styles.impactDecreases
                        )}>
                          {item.impact === "increases_risk" ? "Increases" : "Decreases"} risk
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className={styles.legend}>
          <div className={styles.legendItem}>
            <span className={styles.legendDotRed} />
            <span className={styles.legendLabel}>Increases risk</span>
          </div>
          <div className={styles.legendItem}>
            <span className={styles.legendDotGreen} />
            <span className={styles.legendLabel}>Decreases risk</span>
          </div>
        </div>
      </div>
    </ShimmerBorder>
  );
}
