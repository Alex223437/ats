import React from "react";
import SkeletonBlock from "@/components/LoadingComponents/SkeletonBlock/SkeletonBlock";
import CircleIcon from "@/assets/svg/circle.svg?react";
import "./TradesTable.scss";

export default function TradesTable({ trades = [], loading = false }) {
  const hasData = Array.isArray(trades) && trades.length > 0;

  return (
    <div className="trades-table">
      <h3 className="trades-table__title">Trades Table</h3>

      {loading ? (
        <SkeletonBlock rows={5} />
      ) : !hasData ? (
        <div className="empty-chart">
          <p>No trades available for selected filters.</p>
          <CircleIcon className="empty-icon empty-icon-empty" />
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Ticker</th>
              <th>Action</th>
              <th>Price</th>
              <th>Qty</th>
              <th>Result</th>
              <th>Strategy</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade, index) => (
              <tr key={trade.id}>
                <td>{index + 1}</td>
                <td>{trade.symbol}</td>
                <td>
                  <span
                    className={`badge ${
                      trade.action === "buy" ? "buy" : "sell"
                    }`}
                  >
                    {trade.action.toUpperCase()}
                  </span>
                </td>
                <td>{trade.price}</td>
                <td>{trade.quantity}</td>
                <td>{trade.status || "—"}</td>
                <td>{trade.strategy_title || "—"}</td>
                <td>{new Date(trade.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}