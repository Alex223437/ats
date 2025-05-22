import './AsideLayout.scss';
import AsideLayout from './AsideLayout';
import LoaderSpinner from '@/components/LoadingComponents/LoaderSpinner';

const StrategySidebar = ({
  strategies = [],
  onSelect,
  onCreate,
  selectedStrategy,
  loading
}) => {
  return (
    <AsideLayout title="Strategies">
      {loading ? (
        <div className="loader-wrapper">
          <LoaderSpinner />
          <p style={{ marginTop: '10px', color: '#94a3b8' }}>Loading your strategies...</p>
        </div>
      ) : (
        <>
          <ul className="aside__list">
            {strategies.map((strategy) => (
              <li
                key={strategy.id}
                onClick={() => onSelect(strategy)}
                className={`aside__list-item ${selectedStrategy?.id === strategy.id ? 'active' : ''}`}
              >
                {strategy.title}
              </li>
            ))}
          </ul>
          <button onClick={onCreate} className="aside__btn">
            + Add New
          </button>
        </>
      )}
    </AsideLayout>
  );
};

export default StrategySidebar;