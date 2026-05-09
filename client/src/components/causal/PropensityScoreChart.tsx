"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import { PropensityScore } from "@/lib/api";
import styles from "./PropensityScoreChart.module.scss";

interface PropensityScoreChartProps {
  data: PropensityScore[];
}

interface ChartDataPoint {
  bin: string;
  treated: number;
  control: number;
  balanceRatio: number;
}

export function PropensityScoreChart({ data }: PropensityScoreChartProps) {
  const chartData: ChartDataPoint[] = data.map((item) => ({
    bin: item.bin,
    treated: item.treated_pct * 100,
    control: item.control_pct * 100,
    balanceRatio: item.balance_ratio,
  }));

  return (
    <ShimmerBorder borderRadius="1rem">
      <div className={styles.chartContainer}>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            barGap={2}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255, 255, 255, 0.1)"
              vertical={false}
            />
            <XAxis
              dataKey="bin"
              tick={{ fill: "#9ca3af", fontSize: 10 }}
              tickLine={false}
              axisLine={{ stroke: "rgba(255, 255, 255, 0.2)" }}
            />
            <YAxis
              tick={{ fill: "#9ca3af", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length >= 2) {
                  const treated = payload[0]?.value as number;
                  const control = payload[1]?.value as number;
                  const balanceRatio = payload[0]?.payload?.balanceRatio as number;

                  return (
                    <div className={styles.tooltip}>
                      <p className={styles.tooltipBin}>Bin: {label}</p>
                      <div className={styles.tooltipValues}>
                        <p className={styles.tooltipTreated}>Treated: {treated?.toFixed(1)}%</p>
                        <p className={styles.tooltipControl}>Control: {control?.toFixed(1)}%</p>
                        <p className={styles.tooltipBalance}>Balance: {balanceRatio?.toFixed(2)}</p>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: "12px", paddingTop: "8px" }}
              formatter={(value) => (
                <span className={styles.legendText}>{value}</span>
              )}
            />
            <Bar dataKey="treated" fill="#F3CA40" radius={[2, 2, 0, 0]} name="Treated" />
            <Bar dataKey="control" fill="#06b6d4" radius={[2, 2, 0, 0]} name="Control" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ShimmerBorder>
  );
}
