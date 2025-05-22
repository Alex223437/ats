import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';
import './DashboardOverview.scss';

const MiniChart = ({ data = [], ticker, loading = false }) => {
  if (!ticker) {
    return (
      <div className="mini-chart mini-chart--empty">
        <h3 className="mini-chart__title">No Ticker Selected</h3>
        <p className="mini-chart__placeholder">Select a stock to see the chart</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="mini-chart mini-chart--loading">
        <h3 className="mini-chart__title">{ticker}</h3>
        <div className="loader-wrapper">
          <LoaderSpinner />
          <p style={{ marginTop: '10px', color: '#94a3b8' }}>Loading chart data...</p>
        </div>
      </div>
    );
  }

  if (!data.length) {
    return (
      <div className="mini-chart mini-chart--loading">
        <h3 className="mini-chart__title">{ticker}</h3>
        <p className="mini-chart__placeholder">No chart data available</p>
      </div>
    );
  }

  const last = data[data.length - 1];

  return (
    <div className="mini-chart">
      <div className="mini-chart__header">
        <h3 className="mini-chart__title">{ticker} Recent</h3>
        {last && (
          <div className="mini-chart__metrics">
            <span>{last.Date}</span>
            <span>Price: ${last.Close.toFixed(2)}</span>
          </div>
        )}
      </div>
      <div className="mini-chart-wrapper">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data.slice(-20)}>
            <XAxis dataKey="Date" hide />
            <YAxis domain={['auto', 'auto']} hide />
            <Tooltip
              contentStyle={{
                backgroundColor: '#f1f5f9',
                borderRadius: '10px',
                color: '#1f2937'
              }}
            />
            <Line
              type="monotone"
              dataKey="Close"
              stroke="#e879f9"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default MiniChart;