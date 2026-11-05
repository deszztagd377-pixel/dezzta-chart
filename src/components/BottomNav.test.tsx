import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import BottomNav, { type NavItem } from './BottomNav';

describe('BottomNav', () => {
  it('renders the three supported navigation destinations', () => {
    const markup = renderToStaticMarkup(
      <BottomNav activeItem="chart" onSelect={vi.fn()} />,
    );

    expect(markup).toContain('aria-label="Main navigation"');
    expect(markup).toContain('Watchlist');
    expect(markup).toContain('Chart');
    expect(markup).toContain('Settings');
    expect((markup.match(/<button\b/g) ?? [])).toHaveLength(3);
  });

  it.each<NavItem>(['watchlist', 'chart', 'settings'])(
    'marks only the active %s destination as the current page',
    (activeItem) => {
      const markup = renderToStaticMarkup(
        <BottomNav activeItem={activeItem} onSelect={vi.fn()} />,
      );

      expect((markup.match(/aria-current="page"/g) ?? [])).toHaveLength(1);
      expect(markup).toContain(`aria-label="${activeItem === 'watchlist' ? 'Watchlist' : activeItem === 'chart' ? 'Chart' : 'Settings'}" aria-current="page"`);
    },
  );
});
