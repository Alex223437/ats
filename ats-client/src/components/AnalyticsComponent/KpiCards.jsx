import React from "react";
import "./KpiCards.scss";

const KpiCards = ({ data }) => {
  const cards = [
    { label: "Total PnL", value: `${data?.total_pnl?.toFixed(2) ?? "—"}%`, prefix: data?.total_pnl > 0 ? "+" : "" },
    { label: "Win Rate", value: `${data?.win_rate?.toFixed(0) ?? "—"}%` },
    { label: "Avg. Pott", value: `${data?.average_pnl?.toFixed(2) ?? "—"}` },
    { label: "Max Drawdown", value: `${data?.max_drawdown?.toFixed(2) ?? "—"}`, negative: true },
    { label: "Sharpe Ratio", value: `${data?.sharpe_ratio?.toFixed(2) ?? "—"}` },
  ];

  return (
    <div className="kpi-cards">
      {cards.map((card, idx) => (
        <div className="kpi-card" key={idx}>
          <div className="kpi-card__label">{card.label}</div>
          <div className={`kpi-card__value ${card.negative ? "negative" : ""}`}>
            {card.prefix ?? ""}{card.value}
          </div>
        </div>
      ))}
    </div>
  );
};

export default KpiCards;