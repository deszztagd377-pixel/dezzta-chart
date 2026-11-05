import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import TimeframeSelector from './TimeframeSelector';

describe('TimeframeSelector', () => {
  it('exposes only the daily demo interval as selectable', () => {
    const markup = renderToStaticMarkup(
      <TimeframeSelector selected="1d" onSelect={vi.fn()} />,
    );
    const buttons = markup.match(/<button\b[^>]*>/g) ?? [];
    const disabledButtons = buttons.filter((button) =>
      /\sdisabled(?:="")?/.test(button),
    );

    expect(buttons).toHaveLength(18);
    expect(disabledButtons).toHaveLength(17);
    expect((markup.match(/aria-pressed="true"/g) ?? [])).toHaveLength(1);
    expect(markup).toContain('>1D</button>');
    expect(markup).toContain('SAMPLE DATA: DAILY ONLY');
    expect(markup).toContain('Other intervals are unavailable');
  });

  it('keeps unavailable intervals disabled even when another interval is selected', () => {
    const markup = renderToStaticMarkup(
      <TimeframeSelector selected="1d" onSelect={vi.fn()} />,
    );
    const oneSecondButton = (markup.match(/<button[^>]*>1s<\/button>/) ?? [])[0];

    expect(oneSecondButton).toBeDefined();
    expect(oneSecondButton).toContain('disabled');
    expect(oneSecondButton).toContain('aria-pressed="false"');
  });
});
