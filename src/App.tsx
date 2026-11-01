import React, { useState } from 'react';
import Header from './components/Header';
import BottomNav, { type NavItem } from './components/BottomNav';
import CandlestickChart from './components/CandlestickChart';
import InstrumentCatalogPanel from './components/InstrumentCatalogPanel';
import TimeframeSelector from './components/TimeframeSelector';
import type { Timeframe } from './types';
import './App.css';

const App: React.FC = () => {
  const [timeframe, setTimeframe] = useState<Timeframe>('1d');
  const [activeItem, setActiveItem] = useState<NavItem>('chart');

  return (
    <div className="app-container">
      <Header />

      {activeItem === 'chart' && (
        <>
          <TimeframeSelector selected={timeframe} onSelect={setTimeframe} />
          <main className="main-content">
            <CandlestickChart timeframe={timeframe} />
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
          <section style={{ padding: 20, color: '#9ca3af' }}>
            Settings page is not implemented yet.
          </section>
        </main>
      )}

      <BottomNav activeItem={activeItem} onSelect={setActiveItem} />
    </div>
  );
};

export default App;
