import { useEffect, useState } from 'react';
import { getActiveStrategies, disableStrategy } from '../../services/strategyService';

const ActiveStrategiesPanel = () => {
  const [strategies, setStrategies] = useState([]);

  useEffect(() => {
    getActiveStrategies().then(setStrategies);
  }, []);

  const handleDisable = async (id) => {
    await disableStrategy(id);
    setStrategies(strategies.filter((s) => s.id !== id));
  };

  return (
    <div className="active-strategies">
      <h2>⚙️ Active Strategies</h2>
      {strategies.length === 0 ? (
        <p>No active strategies</p>
      ) : (
        <ul>
          {strategies.map((s) => (
            <li key={s.id}>
              <strong>{s.title}</strong> — {s.automation_mode}, every {s.market_check_frequency}
              <br />
              Applies to: {s.tickers.join(', ')}
              <button onClick={() => handleDisable(s.id)}>❌ Disable</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ActiveStrategiesPanel;
