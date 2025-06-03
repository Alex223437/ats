import React from "react";
import SkeletonBlock from "@/components/LoadingComponents/SkeletonBlock/SkeletonBlock";
import CircleIcon from "@/assets/svg/circle.svg?react";
import "./BacktestTradesTable.scss";

export default function BacktestTradesTable({ trades = [], loading = false }) {
  const hasData = Array.isArray(trades) && trades.length > 0;

  return (
    <div className="trades-table">
      <h3 className="trades-table__title">Trades Table</h3>

      {loading ? (
        <SkeletonBlock rows={5} />
      ) : !hasData ? (
        <div className="empty-chart">
          <p>No trades available for selected period.</p>
          <CircleIcon className="empty-icon empty-icon-empty" />
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Action</th>
              <th>Price</th>
              <th>Result</th>
              <th>PnL</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>
                  <span className={`badge ${trade.action === "buy" ? "buy" : "sell"}`}>
                    {trade.action.toUpperCase()}
                  </span>
                </td>
                <td>{trade.price.toFixed(2)}</td>
                <td>{trade.result.toUpperCase()}</td>
                <td style={{ color: trade.pnl >= 0 ? "#22c55e" : "#ef4444" }}>
                  {trade.pnl >= 0 ? "+" : ""}{trade.pnl.toFixed(2)}%
                </td>
                <td>{new Date(trade.time).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}