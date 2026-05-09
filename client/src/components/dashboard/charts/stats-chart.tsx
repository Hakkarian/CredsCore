"use client";

import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";
import { cn } from "@/lib/utils";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./stats-chart.module.scss";

interface StatsChartProps {
  data: Array<{ label: string; value: number }>;
  title: string;
  color?: string;
  className?: string;
}

export function StatsChart({ data, title, color = "#F3CA40", className }: StatsChartProps) {
  return (
    <ShimmerBorder className={cn("rounded-2xl", className)}>
      <div>
        <h4 className={styles.title}>{title}</h4>
        <div>
          <ResponsiveContainer width="100%" height={80}>
            <AreaChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="label" hide />
              <YAxis hide />
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                fill={`url(#gradient-${title})`}
                strokeWidth={2}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload[0]) {
                    return (
                      <div className={styles.tooltip}>
                        {payload[0].value}
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </ShimmerBorder>
  );
}
