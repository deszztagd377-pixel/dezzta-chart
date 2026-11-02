import React, { useState } from 'react';
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
  const [showGrid, setShowGrid] = useState(true);

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
