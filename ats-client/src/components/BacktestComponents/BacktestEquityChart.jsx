import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { format, parseISO } from "date-fns";
import LoaderSpinner from "@/components/LoadingComponents/LoaderSpinner";
import ArrowIcon from '@/assets/svg/arrow.svg?react';
import "./BacktestEquityChart.scss";

export default function BacktestEquityChart({ data = [], loading = false }) {
  const hasData = Array.isArray(data) && data.length > 0;

  return (
    <div className="equity-chart-card">
      <h3 className="equity-chart-card__title">Backtest Equity Curve</h3>

      {loading ? (
        <div className="loader-wrapper">
          <LoaderSpinner />
          <p style={{ marginTop: "10px", color: "#94a3b8" }}>
            Loading equity curve...
          </p>
        </div>
      ) : !hasData ? (
        <div className="empty-chart">
          <p>No backtest data available</p>
          <ArrowIcon className="empty-icon" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={540}>
          <LineChart data={data} margin={{ left: 0 }}>
            <XAxis
              dataKey="date"
              tickFormatter={(str) => format(parseISO(str), "MMM d")}
              tick={{ fill: "#e0e7ff", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#e0e7ff", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e1b4b",
                border: "1px solid #7c3aed",
                borderRadius: "8px",
                color: "#e0e7ff",
                boxShadow: "0 0 10px rgba(124, 58, 237, 0.4)",
                fontSize: "14px",
              }}
              itemStyle={{ color: "#e0e7ff" }}
              labelStyle={{ color: "#c4b5fd", fontWeight: "bold" }}
            />
            <Line
              type="monotone"
              dataKey="pnl"
              stroke="#7c3aed"
              strokeWidth={3}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}