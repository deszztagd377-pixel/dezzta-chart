import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import BottomNav, { type NavItem } from './components/BottomNav';
import CandlestickChart from './components/CandlestickChart';
import InstrumentCatalogPanel from './components/InstrumentCatalogPanel';
import SettingsPanel from './components/SettingsPanel';
import TimeframeSelector from './components/TimeframeSelector';
import type { Timeframe } from './types';
import './App.css';

const App: React.FC = () => {
  const [timeframe, setTimeframe] = useState<Timeframe>('1d');
  const [activeItem, setActiveItem] = useState<NavItem>('chart');
  const [showGrid, setShowGrid] = useState<boolean>(() => {
    if (typeof window === 'undefined') return true;

    try {
      const savedPreference = window.localStorage.getItem('dezzta-chart:show-grid');
      return savedPreference === null ? true : savedPreference === 'true';
    } catch {
      return true;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem('dezzta-chart:show-grid', String(showGrid));
    } catch {
      // Keep the setting usable for this session when storage is unavailable.
    }
  }, [showGrid]);

  const isChartActive = activeItem === 'chart';

  return (
    <div className="app-container">
      <Header />

      <div
        className={`timeframe-selector-slot ${isChartActive ? '' : 'is-hidden'}`}
        aria-hidden={!isChartActive}
      >
        <TimeframeSelector selected={timeframe} onSelect={setTimeframe} />
      </div>

      <main className="main-content">
        <section
          className={`content-panel ${isChartActive ? 'is-active' : 'is-inactive'}`}
          aria-hidden={!isChartActive}
        >
          <CandlestickChart timeframe={timeframe} showGrid={showGrid} />
        </section>

        {activeItem === 'watchlist' && (
          <section className="content-panel is-active">
            <InstrumentCatalogPanel />
          </section>
        )}

        {activeItem === 'settings' && (
          <section className="content-panel is-active">
            <SettingsPanel
              showGrid={showGrid}
              onShowGridChange={setShowGrid}
              onReset={() => setShowGrid(true)}
            />
          </section>
        )}
      </main>

      <BottomNav activeItem={activeItem} onSelect={setActiveItem} />
    </div>
  );
};

export default App;
