import React from 'react';
import { BarChart3, LineChart, Settings } from 'lucide-react';
import './BottomNav.css';

export type NavItem = 'watchlist' | 'chart' | 'settings';

interface BottomNavProps {
  activeItem: NavItem;
  onSelect: (item: NavItem) => void;
}

const BottomNav: React.FC<BottomNavProps> = ({ activeItem, onSelect }) => {
  const navItems = [
    { id: 'watchlist' as NavItem, label: 'Watchlist', icon: BarChart3 },
    { id: 'chart' as NavItem, label: 'Chart', icon: LineChart },
    { id: 'settings' as NavItem, label: 'Settings', icon: Settings },
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
            onClick={() => onSelect(item.id)}
            aria-label={item.label}
            aria-current={isActive ? 'page' : undefined}
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
