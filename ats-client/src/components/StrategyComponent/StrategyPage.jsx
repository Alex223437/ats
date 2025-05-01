import { useState, useEffect } from 'react';
import {
  fetchStrategies,
  createStrategy,
  updateStrategy,
  deleteStrategy,
} from '../../services/strategyService';
import StrategyForm from './StrategyForm';
import StrategySidebar from '../AsideComponent/AsideStrategy';

const StrategyPage = () => {
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState(null);

  useEffect(() => {
    const loadStrategies = async () => {
      const data = await fetchStrategies();
      setStrategies(data);
    };
    loadStrategies();
  }, []);

  const handleSave = async (strategy) => {
    if (selectedStrategy) {
      await updateStrategy(selectedStrategy.id, strategy);
    } else {
      await createStrategy(strategy);
    }
    setSelectedStrategy(null);
    const updatedStrategies = await fetchStrategies();
    setStrategies(updatedStrategies);
  };

  const handleDelete = async (strategyId) => {
    await deleteStrategy(strategyId);
    setSelectedStrategy(null);
    const updatedStrategies = await fetchStrategies();
    setStrategies(updatedStrategies);
  };

  return (
    <>
      <StrategySidebar
        strategies={strategies}
        onSelect={setSelectedStrategy}
        onCreate={() => setSelectedStrategy(null)}
        selectedStrategy={selectedStrategy}
      />
      <StrategyForm strategy={selectedStrategy} onSave={handleSave} onDelete={handleDelete} />
    </>
  );
};

export default StrategyPage;
