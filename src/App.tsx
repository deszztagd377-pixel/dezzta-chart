import React from 'react';
import Header from './components/Header';
import BottomNav from './components/BottomNav';
import ChartPlaceholder from './components/ChartPlaceholder';
import './App.css';

const App: React.FC = () => {
  return (
    <div className="app-container">
      <Header />
      <main className="main-content">
        <ChartPlaceholder />
      </main>
      <BottomNav />
    </div>
  );
};

export default App;