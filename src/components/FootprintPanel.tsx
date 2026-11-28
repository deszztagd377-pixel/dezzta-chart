import React, { useMemo, useState } from 'react';
import './FootprintPanel.css';

type FootprintSide = 'bid' | 'ask';
interface FootprintLevel {
  price: number;
  bid: number;
  ask: number;
}
interface SelectedCell extends FootprintLevel {
  side: FootprintSide;
}
const SAMPLE_LEVELS: FootprintLevel[] = [
  { price: 4035.00, bid: 8200, ask: 15100 },
  { price: 4034.75, bid: 19300, ask: 5200 },
  { price: 4034.50, bid: 5600, ask: 24400 },
  { price: 4034.25, bid: 0, ask: 15000 },
  { price: 4034.00, bid: 32000, ask: 48000 },
  { price: 4033.75, bid: 47000, ask: 24000 },
  { price: 4033.50, bid: 38000, ask: 22000 },
  { price: 4033.25, bid: 12000, ask: 34000 },
];

const formatVolume = (value: number): string => {
  const absolute = Math.abs(value);
  return absolute >= 1000
    ? `${(absolute / 1000).toFixed(absolute % 1000 === 0 ? 0 : 1)}k`
    : String(absolute);
};
const formatSigned = (value: number): string =>
  `${value > 0 ? '+' : value < 0 ? '-' : ''}${formatVolume(value)}`;

export const getFootprintCellMetrics = (cell: SelectedCell) => {
  const total = cell.bid + cell.ask;
  const delta = cell.ask - cell.bid;
  return {
    total,
    delta,
    deltaPercent: total === 0 ? 0 : (delta / total) * 100,
    imbalance: cell.bid === 0 ? (cell.ask > 0 ? 'ASK DOMINANT' : 'BALANCED')
      : cell.ask / cell.bid >= 3 ? 'ASK IMBALANCE'
      : cell.bid / Math.max(cell.ask, 1) >= 3 ? 'BID IMBALANCE'
      : 'BALANCED',
  };
};

const FootprintPanel: React.FC = () => {
  const [selected, setSelected] = useState<SelectedCell>({
    ...SAMPLE_LEVELS[4], side: 'ask',
  });
  const metrics = useMemo(() => getFootprintCellMetrics(selected), [selected]);

  return (
    <section className="footprint-panel" aria-label="Footprint order-flow panel">
      <header className="footprint-header">
        <div>
          <strong>FOOTPRINT PRO</strong>
          <span className="footprint-demo-tag">SIMULATED DATA · NOT LIVE</span>
        </div>
        <span className="footprint-instruction">Tap any bid / ask cell for details</span>
      </header>
      <div className="footprint-grid-wrap">
        <div className="footprint-column-head"><span>PRICE</span><span>BID</span><span>ASK</span><span>DELTA</span></div>
        {SAMPLE_LEVELS.map((level) => {
          const delta = level.ask - level.bid;
          return (
            <div className="footprint-row" key={level.price}>
              <span className="footprint-price">{level.price.toFixed(2)}</span>
              <button
                type="button"
                className={`footprint-cell bid-cell ${selected.price === level.price && selected.side === 'bid' ? 'is-selected' : ''}`}
                aria-label={`Select bid ${formatVolume(level.bid)} at ${level.price.toFixed(2)}`}
                aria-pressed={selected.price === level.price && selected.side === 'bid'}
                onClick={() => setSelected({ ...level, side: 'bid' })}
              >{formatVolume(level.bid)}</button>
              <button
                type="button"
                className={`footprint-cell ask-cell ${selected.price === level.price && selected.side === 'ask' ? 'is-selected' : ''}`}
                aria-label={`Select ask ${formatVolume(level.ask)} at ${level.price.toFixed(2)}`}
                aria-pressed={selected.price === level.price && selected.side === 'ask'}
                onClick={() => setSelected({ ...level, side: 'ask' })}
              >{formatVolume(level.ask)}</button>
              <span className={`footprint-delta ${delta >= 0 ? 'positive' : 'negative'}`}>{formatSigned(delta)}</span>
            </div>
          );
        })}
      </div>
      <aside className="footprint-detail" aria-live="polite" aria-label="Selected footprint cell details">
        <div className="footprint-detail-title">
          <strong>{selected.price.toFixed(2)}</strong>
          <span>{selected.side.toUpperCase()} CELL SELECTED</span>
        </div>
        <div className="footprint-metrics">
          <div><span>DELTA</span><strong className={metrics.delta >= 0 ? 'positive' : 'negative'}>{formatSigned(metrics.delta)}</strong></div>
          <div><span>BID VOLUME</span><strong>{formatVolume(selected.bid)}</strong></div>
          <div><span>ASK VOLUME</span><strong>{formatVolume(selected.ask)}</strong></div>
          <div><span>TOTAL VOLUME</span><strong>{formatVolume(metrics.total)}</strong></div>
          <div><span>DELTA %</span><strong>{metrics.deltaPercent.toFixed(2)}%</strong></div>
          <div><span>IMBALANCE</span><strong>{metrics.imbalance}</strong></div>
        </div>
        <p>Values are illustrative fixtures. Real footprint requires validated trade-level bid/ask aggressor data.</p>
      </aside>
    </section>
  );
};
export default FootprintPanel;
