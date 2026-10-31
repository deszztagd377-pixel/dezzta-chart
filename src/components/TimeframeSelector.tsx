
import React from 'react';
import type { Timeframe } from '../types';
import './TimeframeSelector.css';

interface TimeframeSelectorProps {
  selected: Timeframe;
  onSelect: (timeframe: Timeframe) => void;
}

const timeframes: Timeframe[] = [
  '1s', '5s', '15s', '30s', '45s',
  '1m', '3m', '5m', '15m', '30m', '45m',
  '1h', '2h', '4h',
  '1d', '1w', '1M', '3M',
];

const TimeframeSelector: React.FC<TimeframeSelectorProps> = ({
  selected,
  onSelect,
}) => {
  const getLabel = (timeframe: Timeframe) => {
    if (timeframe.endsWith('d')) return timeframe.replace('d', 'D');
    if (timeframe.endsWith('w')) return timeframe.replace('w', 'W');
    return timeframe;
  };

  return (
    <div className="timeframe-selector">
      {timeframes.map((timeframe) => (
        <button
          key={timeframe}
          type="button"
          className={`timeframe-button ${
            selected === timeframe ? 'active' : ''
          }`}
          onClick={() => onSelect(timeframe)}
          aria-pressed={selected === timeframe}
        >
          {getLabel(timeframe)}
        </button>
      ))}
    </div>
  );
};

export default TimeframeSelector;
