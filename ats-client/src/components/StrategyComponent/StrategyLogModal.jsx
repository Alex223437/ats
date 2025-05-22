import React, { useState } from 'react';
import './StrategyLogModal.scss';

const StrategyLogModal = ({ isOpen, onClose, logs = [], strategyTitle }) => {
  const [expandedId, setExpandedId] = useState(null);
  if (!isOpen) return null;

  const toggleDebug = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="overview-card" onClick={(e) => e.stopPropagation()}>
        <div className="overview-card__title">
          Logs for <strong>{strategyTitle}</strong>
        </div>
        <div className="overview-card__content">
          {logs.length === 0 ? (
            <p>No logs found for this strategy.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Action</th>
                  <th>Price</th>
                  <th>Executed</th>
                  <th>Status</th>
                  <th>Time</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <React.Fragment key={log.id}>
                    <tr>
                      <td>{log.ticker}</td>
                      <td>
                        <span className={`signal-tag ${log.action || 'hold'}`}>
                          {log.action?.toUpperCase() || 'HOLD'}
                        </span>
                      </td>
                      <td>${log.price?.toFixed(2) || '—'}</td>
                      <td>{log.executed ? '✅' : '❌'}</td>
                      <td>{log.result || '—'}</td>
                      <td>{new Date(log.created_at).toLocaleString()}</td>
                      <td>
                        <button
                          style={{ fontSize: '12px', padding: '4px 8px' }}
                          onClick={() => toggleDebug(log.id)}
                        >
                          {expandedId === log.id ? 'Hide' : 'Details'}
                        </button>
                      </td>
                    </tr>
                    {expandedId === log.id && (
                      <tr>
                        <td colSpan="7">
                          <pre className="debug-json">
                            {JSON.stringify(log.debug_data, null, 2)}
                          </pre>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          )}
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default StrategyLogModal;