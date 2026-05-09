"use client";

import { LineChart, Line, ResponsiveContainer } from "recharts";

interface MiniSparklineProps {
  data: { value: number }[];
  color?: string;
}

export function MiniSparkline({ data, color }: MiniSparklineProps) {
  const strokeColor = color || "#4ade80";

  return (
    <ResponsiveContainer width="100%" height={30}>
      <LineChart data={data}>
        <Line
          type="monotone"
          dataKey="value"
          stroke={strokeColor}
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
