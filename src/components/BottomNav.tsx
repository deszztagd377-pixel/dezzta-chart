import React, { useState } from 'react';
import { BarChart3, LineChart, Settings } from 'lucide-react';
import './BottomNav.css';

type NavItem = 'watchlist' | 'chart' | 'settings';

const BottomNav: React.FC = () => {
  const [activeItem, setActiveItem] = useState<NavItem>('chart');

  const navItems = [
    { id: 'watchlist' as NavItem, label: 'Watchlist', icon: BarChart3 },
    { id: 'chart' as NavItem, label: 'Chart', icon: LineChart },
    { id: 'settings' as NavItem, label: 'Settings', icon: Settings }
  ];

  return (
    <nav className="bottom-nav">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeItem === item.id;
        return (
          <button
            key={item.id}
            className={`nav-item ${isActive ? 'active' : ''}`}
            onClick={() => setActiveItem(item.id)}
            aria-label={item.label}
          >
            <Icon size={20} strokeWidth={isActive ? 2.5 : 2} />
            <span className="nav-label">{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
};

export default BottomNav;