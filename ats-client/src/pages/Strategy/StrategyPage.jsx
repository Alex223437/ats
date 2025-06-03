import { useEffect, useState } from 'react';
import StrategyForm from '../../components/StrategyComponent/StrategyForm';
import StrategySidebar from '../../components/AsideComponent/AsideStrategy';
import ManageStrategies from '../../components/StrategyComponent/ManageStrategies';
import ActiveStrategies from '../../components/StrategyComponent/ActiveStrategies';
import StrategyLogModal from '../../components/StrategyComponent/StrategyLogModal';
import TensorFlowStrategyForm from '../../components/StrategyComponent/TensorFlowForm';
import useStrategyApi from '@/hooks/useStrategyApi';
import useStrategyLogs from '../../hooks/useStrategyLogs';
import { toast } from 'react-hot-toast';

import './StrategyPage.scss';

const StrategyPage = () => {
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [logsModal, setLogsModal] = useState({ open: false, logs: [], title: '' });

  const {
    fetchStrategies,
    createStrategy,
    updateStrategy,
    deleteStrategy,
    enableStrategy,
    disableStrategy,
    setStrategyTickers,
    fetchStrategyTickers,
    loading,
    strategies,
    refreshStrategies,
    trainStrategyModel,
    deleteTrainedModel,
    fetchModelInfo
  } = useStrategyApi();

  const { fetchStrategyLogs } = useStrategyLogs();

  useEffect(() => {
    fetchStrategies();
  }, []);

  useEffect(() => {
    if (!selectedStrategy) return;
    const updated = strategies.find((s) => s.id === selectedStrategy.id);
    if (updated) setSelectedStrategy(updated);
  }, [strategies]);

  const handleSave = async (strategy, selectedTickers = []) => {
    let savedStrategy;
    if (selectedStrategy) {
      savedStrategy = await updateStrategy(selectedStrategy.id, strategy);
    } else {
      savedStrategy = await createStrategy(strategy);
    }

    if (savedStrategy?.id && selectedTickers.length) {
      await setStrategyTickers(savedStrategy.id, selectedTickers);
    }

    const updatedList = await refreshStrategies();
    const updated = updatedList.find((s) => s.id === savedStrategy.id);
    setSelectedStrategy(updated);
    return updated;
  };

  const handleDelete = async (strategyId) => {
    try {
      await deleteStrategy(strategyId);
      setSelectedStrategy(null);
      await refreshStrategies();
      toast.success('Strategy deleted successfully!');
    } catch (err) {
      toast.error('Failed to delete strategy');
    }
  };

  const handleStart = async (strategyId) => {
    await enableStrategy(strategyId);
    await refreshStrategies();
  };

  const handleStop = async (strategyId) => {
    await disableStrategy(strategyId);
    await refreshStrategies();
  };

  const handleViewLogs = async (strategyId) => {
    const logs = await fetchStrategyLogs(strategyId);
    const strategy = strategies.find((s) => s.id === strategyId);

    if (!logs || logs.length === 0) {
      toast.error('No logs found for this strategy');
      return;
    }

    setLogsModal({ open: true, logs, title: strategy?.title || '' });
  };

  const handleTrainClick = async () => {
    try {
      await trainStrategyModel(selectedStrategy.id);
      await refreshStrategies();
      toast.success('Model trained successfully!');
    } catch (err) {
      toast.error('Training failed');
    }
  };

  const handleDeleteModel = async () => {
    try {
      await deleteTrainedModel(selectedStrategy.id);
      await refreshStrategies();
      toast.success('Model deleted successfully!');
    } catch (err) {
      toast.error('Failed to delete model');
    }
  };

  return (
    <>
      <StrategySidebar
        strategies={strategies}
        onSelect={setSelectedStrategy}
        onCreate={() => setSelectedStrategy(null)}
        selectedStrategy={selectedStrategy}
        loading={loading.fetch}
      />
      <div className="strategy-grid">
        {selectedStrategy?.strategy_type === 'ml_tf' ? (
          <TensorFlowStrategyForm
            strategy={selectedStrategy}
            onSave={handleSave}
            onDelete={handleDelete}
            loading={loading.create || loading.update || loading.fetch}
            onTrain={handleTrainClick}
            onDeleteModel={handleDeleteModel}
          />
        ) : (
          <StrategyForm
            strategy={selectedStrategy}
            onSave={handleSave}
            onDelete={handleDelete}
            loading={loading.create || loading.update || loading.fetch}
          />
        )}
        <ManageStrategies
          strategies={strategies}
          onStart={handleStart}
          onStop={handleStop}
          loading={loading.fetch}
        />
        <ActiveStrategies
          strategies={strategies}
          onStop={handleStop}
          onViewLogs={handleViewLogs}
        />
      </div>
      <StrategyLogModal
        isOpen={logsModal.open}
        onClose={() => setLogsModal({ open: false, logs: [], title: '' })}
        logs={logsModal.logs}
        strategyTitle={logsModal.title}
      />
    </>
  );
};

export default StrategyPage;