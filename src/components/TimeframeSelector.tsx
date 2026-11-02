import React from 'react';
import type { Timeframe } from '../types';
import './TimeframeSelector.css';

interface TimeframeSelectorProps {
  selected: Timeframe;
  onSelect: (timeframe: Timeframe) => void;
}

// The current chart fixture contains daily date-only candles.
// Other intervals remain visible as planned options, but are unavailable
// until a verified dataset at the requested resolution is connected.
const timeframes: Timeframe[] = [
  '1s', '5s', '15s', '30s', '45s',
  '1m', '3m', '5m', '15m', '30m', '45m',
  '1h', '2h', '4h',
  '1d', '1w', '1M', '3M',
];

const availableSampleTimeframes = new Set<Timeframe>(['1d']);

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
    <div className="timeframe-selector-wrap">
      <div
        className="timeframe-selector"
        role="group"
        aria-label="Chart interval"
        aria-describedby="timeframe-data-note"
      >
        {timeframes.map((timeframe) => {
          const isAvailable = availableSampleTimeframes.has(timeframe);
          const isSelected = selected === timeframe;

          return (
            <button
              key={timeframe}
              type="button"
              className={`timeframe-button ${
                isSelected ? 'active' : ''
              } ${!isAvailable ? 'unavailable' : ''}`}
              onClick={() => {
                if (isAvailable) onSelect(timeframe);
              }}
              disabled={!isAvailable}
              aria-pressed={isSelected}
              title={
                isAvailable
                  ? 'Available for the current daily sample dataset'
                  : 'Unavailable: verified data at this interval is not connected'
              }
            >
              {getLabel(timeframe)}
            </button>
          );
        })}
      </div>
      <p className="timeframe-data-note" id="timeframe-data-note">
        SAMPLE DATA: DAILY ONLY · Other intervals are unavailable until matching data is verified.
      </p>
    </div>
  );
};

export default TimeframeSelector;
