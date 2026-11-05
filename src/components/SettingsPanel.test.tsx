import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import SettingsPanel from './SettingsPanel';

vi.mock('../auth/AuthProvider', () => ({
  useAuth: () => ({
    user: null,
    status: 'unconfigured',
    error: null,
    signInEmail: vi.fn(async () => undefined),
    registerEmail: vi.fn(async () => undefined),
    signInGoogle: vi.fn(async () => undefined),
    signOutUser: vi.fn(async () => undefined),
    clearError: vi.fn(),
  }),
}));

describe('SettingsPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the display preference with its accessible label and checked state', () => {
    const markup = renderToStaticMarkup(
      <SettingsPanel showGrid onShowGridChange={vi.fn()} onReset={vi.fn()} />,
    );

    expect(markup).toContain('aria-label="Show chart grid lines"');
    expect(markup).toMatch(/type="checkbox"[^>]*checked=""/);
    expect(markup).toContain('Grid lines');
  });

  it('renders the unchecked display preference without marking it checked', () => {
    const markup = renderToStaticMarkup(
      <SettingsPanel showGrid={false} onShowGridChange={vi.fn()} onReset={vi.fn()} />,
    );
    const checkbox = markup.match(/<input[^>]*type="checkbox"[^>]*>/)?.[0];

    expect(checkbox).toBeDefined();
    expect(checkbox).not.toContain('checked');
  });

  it('keeps the sample-data disclosure and reset action visible', () => {
    const markup = renderToStaticMarkup(
      <SettingsPanel showGrid onShowGridChange={vi.fn()} onReset={vi.fn()} />,
    );

    expect(markup).toContain('Data status');
    expect(markup).toContain('DEMO');
    expect(markup).toContain('fixed sample dataset');
    expect(markup).toContain('Restore display defaults');
  });
});
