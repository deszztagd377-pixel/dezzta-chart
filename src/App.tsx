
import React from 'react';
import Header from './components/Header';
import BottomNav from './components/BottomNav';
import CandlestickChart from './components/CandlestickChart';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="app-container">
      <Header />

      <main className="main-content">
        <CandlestickChart />
      </main>

      <BottomNav />
    </div>
  );
};

export default App;
