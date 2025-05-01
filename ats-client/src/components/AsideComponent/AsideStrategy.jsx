import './AsideLayout.scss';
import AsideLayout from './AsideLayout';

const StrategySidebar = ({ strategies, onSelect, onCreate, selectedStrategy }) => {
  return (
    <AsideLayout title="Strategies">
      <ul className="aside__list">
        {strategies.map((strategy) => (
          <li
            key={strategy.id}
            onClick={() => onSelect(strategy)}
            className={`aside__list-item ${selectedStrategy === strategy ? 'active' : ''}`}
          >
            {strategy.title}
          </li>
        ))}
      </ul>
      <button onClick={onCreate} className="aside__btn">
        + Add New
      </button>
    </AsideLayout>
  );
};

export default StrategySidebar;
