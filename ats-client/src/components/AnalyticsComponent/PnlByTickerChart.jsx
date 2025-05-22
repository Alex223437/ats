import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import LoaderSpinner from "@/components/LoadingComponents/LoaderSpinner";
import ArrowIcon from "@/assets/svg/arrow1.svg?react";
import "./PnLByTickerChart.scss";

const COLORS = {
  positive: "#7c3aed", // фиолетовый
  negative: "#f87171", // красный
};

export default function PnLByTickerChart({ data = [], loading = false }) {
  const hasData = Array.isArray(data) && data.length > 0;

  return (
    <div className="chart-card">
      <h3 className="chart-card__title">PnL by Ticker</h3>

      {loading ? (
        <div className="loader-wrapper">
          <LoaderSpinner />
          <p style={{ marginTop: "10px", color: "#94a3b8" }}>
            Loading PnL data...
          </p>
        </div>
      ) : !hasData ? (
        <div className="empty-chart">
          <p>No PnL data available for selected filters.</p>
          <ArrowIcon className="empty-icon" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 0, right: 20, bottom: 0, left: 20 }}
          >
            <XAxis
              type="number"
              tick={{ fill: "#e0e7ff", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              dataKey="symbol"
              type="category"
              tick={{ fill: "#e0e7ff", fontSize: 14 }}
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
              cursor={false}
              itemStyle={{ color: "#e0e7ff" }}
              labelStyle={{ color: "#c4b5fd", fontWeight: "bold" }}
            />
            <Bar dataKey="pnl" radius={[8, 8, 8, 8]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.pnl >= 0 ? COLORS.positive : COLORS.negative}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}