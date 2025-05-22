import { useState } from "react";
import { useNavigate } from "react-router-dom";
import OverviewCard from "./OverviewCard";
import SkeletonBlock from "@/components/LoadingComponents/SkeletonBlock/SkeletonBlock";
import CrossIcon from "@/assets/svg/cross.svg?react";
import { disconnectBroker } from "@/services/userService";
import "./DashboardOverview.scss";

const BrokerStatus = ({ broker, loading, setBrokerInfo }) => {
  const [disconnecting, setDisconnecting] = useState(false);
  const navigate = useNavigate();

  const handleDisconnect = async () => {
    if (!window.confirm("Are you sure you want to disconnect your broker?")) return;
    setDisconnecting(true);
    await disconnectBroker();
    setBrokerInfo(null);
    setDisconnecting(false);
  };

  if (loading) {
    return (
      <OverviewCard title="Broker Connection">
        <SkeletonBlock rows={6} />
      </OverviewCard>
    );
  }

  if (!broker || !broker.account_status) {
    return (
      <OverviewCard title="Broker Connection">
        <div className="empty-orders empty-strategies">
          <CrossIcon className="empty-svg empty-svg-fill" />
          <div className="empty-block">
            <p className="empty-text">Broker is not connected</p>
            <p className="empty-subtext">To see trading data, please connect your broker</p>
            <button className="empty-btn" onClick={() => navigate('/settings')}>
              Go to Settings
            </button>
          </div>
        </div>
      </OverviewCard>
    );
  }

  const format = (val) =>
    typeof val === "number" || !isNaN(parseFloat(val))
      ? `$${parseFloat(val).toFixed(2)}`
      : "—";

  return (
    <OverviewCard title="Broker Connection">
      <table className="table">
        <tbody>
          <tr>
            <td>Status:</td>
            <td>Connected</td>
          </tr>
          <tr>
            <td>Account:</td>
            <td><strong>{broker.account_status}</strong></td>
          </tr>
          <tr>
            <td>Cash:</td>
            <td>{format(broker.cash)}</td>
          </tr>
          <tr>
            <td>Portfolio:</td>
            <td>{format(broker.portfolio_value)}</td>
          </tr>
          <tr>
            <td>Buying Power:</td>
            <td>{format(broker.buying_power)}</td>
          </tr>
          <tr>
            <td>Today PnL:</td>
            <td style={{ color: broker.today_pnl > 0 ? "#22c55e" : "#ef4444" }}>
              {broker.today_pnl != null ? `${broker.today_pnl > 0 ? "+" : ""}${format(broker.today_pnl)}` : "—"}
            </td>
          </tr>
          <tr>
            <td>Total PnL:</td>
            <td style={{ color: broker.total_pnl > 0 ? "#22c55e" : "#ef4444" }}>
              {broker.total_pnl != null ? `${broker.total_pnl > 0 ? "+" : ""}${format(broker.total_pnl)}` : "—"}
            </td>
          </tr>
        </tbody>
      </table>
      <button onClick={handleDisconnect} disabled={disconnecting}>
        {disconnecting ? "Disconnecting..." : "Disconnect"}
      </button>
    </OverviewCard>
  );
};

export default BrokerStatus;