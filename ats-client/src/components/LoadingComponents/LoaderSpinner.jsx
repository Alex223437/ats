const LoaderSpinner = ({ size = 60, color = '#c084fc' }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 800 800"
      xmlns="http://www.w3.org/2000/svg"
      style={{ display: 'block' }}
    >
      <style>
        {`
          @keyframes spin {
            to {
              transform: rotate(360deg);
            }
          }

          .spin {
            transform-origin: center;
            animation: spin 1.8s linear infinite;
          }
        `}
      </style>
      <circle
        className="spin"
        cx="400"
        cy="400"
        fill="none"
        r="184"
        strokeWidth="57"
        stroke={color}
        strokeDasharray="706 1400"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default LoaderSpinner;