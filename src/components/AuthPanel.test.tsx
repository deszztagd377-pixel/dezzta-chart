import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AuthPanel from './AuthPanel';

const authMocks = vi.hoisted(() => ({
  useAuth: vi.fn(),
}));

vi.mock('../auth/AuthProvider', () => ({
  useAuth: authMocks.useAuth,
}));

const baseAuth = {
  user: null,
  status: 'unconfigured' as const,
  error: null,
  signInEmail: vi.fn(async () => undefined),
  registerEmail: vi.fn(async () => undefined),
  signInGoogle: vi.fn(async () => undefined),
  signOutUser: vi.fn(async () => undefined),
  clearError: vi.fn(),
};

beforeEach(() => {
  vi.clearAllMocks();
  authMocks.useAuth.mockReturnValue({ ...baseAuth });
});

describe('AuthPanel status presentation', () => {
  it('shows an explicit authentication error instead of reporting signed out', () => {
    authMocks.useAuth.mockReturnValue({
      ...baseAuth,
      status: 'error',
      error: 'Autentikasi gagal.',
    });

    const markup = renderToStaticMarkup(<AuthPanel />);

    expect(markup).toContain('AUTH ERROR');
    expect(markup).not.toContain('SIGNED OUT');
    expect(markup).toContain('role="alert"');
  });

  it('keeps unconfigured Firebase distinct from a signed-out account', () => {
    const markup = renderToStaticMarkup(<AuthPanel />);

    expect(markup).toContain('NOT CONFIGURED');
    expect(markup).not.toContain('SIGNED OUT');
  });

  it('disables every sign-in action while Firebase is not configured', () => {
    const markup = renderToStaticMarkup(<AuthPanel />);
    const actionButtons = [...markup.matchAll(/<button\\b[^>]*>/g)].map(([button]) => button);

    expect(actionButtons).toHaveLength(3);
    expect(actionButtons.every((button) => button.includes('disabled=""'))).toBe(true);
  });

  it('shows signed-in state when the provider has an authenticated user', () => {
    authMocks.useAuth.mockReturnValue({
      ...baseAuth,
      user: { displayName: 'Test User', email: 'test@example.com' },
      status: 'signed-in',
    });

    const markup = renderToStaticMarkup(<AuthPanel />);

    expect(markup).toContain('SIGNED IN');
    expect(markup).toContain('test@example.com');
  });
});
