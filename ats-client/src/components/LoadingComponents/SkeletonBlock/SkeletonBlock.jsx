import './SkeletonBlock.scss';

const SkeletonBlock = ({ rows = 5 }) => {
  return (
    <div className="skeleton-table">
      {[...Array(rows)].map((_, i) => (
        <div key={i} className="skeleton-row" />
      ))}
    </div>
  );
};

export default SkeletonBlock;