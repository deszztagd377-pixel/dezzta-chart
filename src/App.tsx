import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import BottomNav, { type NavItem } from './components/BottomNav';
import CandlestickChart from './components/CandlestickChart';
import InstrumentCatalogPanel from './components/InstrumentCatalogPanel';
import SettingsPanel from './components/SettingsPanel';
import TimeframeSelector from './components/TimeframeSelector';
import type { Timeframe } from './types';
import {
  readBooleanPreference,
  writeBooleanPreference,
  SHOW_GRID_STORAGE_KEY,
} from './utils/preferences';
import './App.css';

const App: React.FC = () => {
  const [timeframe, setTimeframe] = useState<Timeframe>('1d');
  const [activeItem, setActiveItem] = useState<NavItem>('chart');
  const [showGrid, setShowGrid] = useState<boolean>(() =>
    readBooleanPreference(() => window.localStorage, SHOW_GRID_STORAGE_KEY, true),
  );

  useEffect(() => {
    writeBooleanPreference(() => window.localStorage, SHOW_GRID_STORAGE_KEY, showGrid);
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
