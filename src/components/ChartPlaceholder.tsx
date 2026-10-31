import React from 'react';
import './ChartPlaceholder.css';

const ChartPlaceholder: React.FC = () => {
  return (
    <div className="chart-placeholder">
      <div className="chart-content">
        <div className="chart-title">Chart View</div>
        <div className="chart-subtitle">Select a symbol to begin</div>
      </div>
    </div>
  );
};

export default ChartPlaceholder;