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

  return (
    <div className="app-container">
      <Header />

      {activeItem === 'chart' && (
        <>
          <TimeframeSelector selected={timeframe} onSelect={setTimeframe} />
          <main className="main-content">
            <CandlestickChart timeframe={timeframe} showGrid={showGrid} />
          </main>
        </>
      )}

      {activeItem === 'watchlist' && (
        <main className="main-content">
          <InstrumentCatalogPanel />
        </main>
      )}

      {activeItem === 'settings' && (
        <main className="main-content">
          <SettingsPanel
            showGrid={showGrid}
            onShowGridChange={setShowGrid}
            onReset={() => setShowGrid(true)}
          />
        </main>
      )}

      <BottomNav activeItem={activeItem} onSelect={setActiveItem} />
    </div>
  );
};

export default App;
