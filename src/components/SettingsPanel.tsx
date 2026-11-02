import React from 'react';
import './SettingsPanel.css';

interface SettingsPanelProps {
  showGrid: boolean;
  onShowGridChange: (enabled: boolean) => void;
  onReset: () => void;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  showGrid,
  onShowGridChange,
  onReset,
}) => (
  <section className="settings-panel" aria-labelledby="settings-title">
    <div className="settings-panel__heading">
      <p className="settings-panel__eyebrow">PREFERENCES</p>
      <h2 id="settings-title">Chart settings</h2>
      <p className="settings-panel__intro">
        Adjust the chart display. These options change presentation only; they do not
        connect a market-data provider or place orders.
      </p>
    </div>

    <section className="settings-panel__section" aria-labelledby="display-title">
      <div className="settings-panel__section-heading">
        <h3 id="display-title">Display</h3>
        <span>CHART</span>
      </div>

      <label className="settings-panel__toggle">
        <span className="settings-panel__toggle-copy">
          <strong>Grid lines</strong>
          <small>Show or hide the chart's horizontal and vertical guides</small>
        </span>
        <input
          type="checkbox"
          checked={showGrid}
          onChange={(event) => onShowGridChange(event.target.checked)}
          aria-label="Show chart grid lines"
        />
      </label>
    </section>

    <section className="settings-panel__section" aria-labelledby="data-title">
      <div className="settings-panel__section-heading">
        <h3 id="data-title">Data status</h3>
        <span className="settings-panel__status">DEMO</span>
      </div>
      <p className="settings-panel__note">
        The current chart uses a fixed sample dataset. It is not live, delayed, or
        exchange-sourced market data. This status remains visible to avoid confusion.
      </p>
    </section>

    <button className="settings-panel__reset" type="button" onClick={onReset}>
      Restore display defaults
    </button>
  </section>
);

export default SettingsPanel;
