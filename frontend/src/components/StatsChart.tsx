"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { ChannelStats } from "@/lib/api";

interface StatsChartProps {
  data: ChannelStats[];
  dataKey: "subscriber_count" | "view_count" | "video_count";
  title: string;
  color: string;
}

export default function StatsChart({
  data,
  dataKey,
  title,
  color,
}: StatsChartProps) {
  const chartData = data
    .slice()
    .reverse()
    .map((stat) => ({
      date: new Date(stat.recorded_at).toLocaleDateString("ja-JP", {
        month: "short",
        day: "numeric",
      }),
      value: stat[dataKey],
    }));

  const formatValue = (value: number): string => {
    if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + "M";
    } else if (value >= 1000) {
      return (value / 1000).toFixed(1) + "K";
    }
    return value.toString();
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={formatValue} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value: number) => [formatValue(value), title]}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
