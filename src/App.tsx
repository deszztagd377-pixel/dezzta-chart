

import React, { useState } from 'react';
import Header from './components/Header';
import BottomNav from './components/BottomNav';
import CandlestickChart from './components/CandlestickChart';
import TimeframeSelector from './components/TimeframeSelector';
import type { Timeframe } from './types';
import './App.css';

const App: React.FC = () => {
  const [timeframe, setTimeframe] = useState<Timeframe>('1d');

  return (
    <div className="app-container">
      <Header />

      <TimeframeSelector
        selected={timeframe}
        onSelect={setTimeframe}
      />

      <main className="main-content">
        <CandlestickChart />
      </main>

      <BottomNav />
    </div>
  );
};

export default App;
