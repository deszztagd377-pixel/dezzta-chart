import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { Auth, User } from 'firebase/auth';

const firebaseMocks = vi.hoisted(() => ({
  getFirebaseAuth: vi.fn(),
  isFirebaseConfigured: vi.fn(),
  onIdTokenChanged: vi.fn(),
}));

vi.mock('../services/firebase', () => ({
  getFirebaseAuth: firebaseMocks.getFirebaseAuth,
  isFirebaseConfigured: firebaseMocks.isFirebaseConfigured,
  createGoogleProvider: vi.fn(),
}));

vi.mock('firebase/auth', () => ({
  createUserWithEmailAndPassword: vi.fn(),
  onIdTokenChanged: firebaseMocks.onIdTokenChanged,
  signInWithEmailAndPassword: vi.fn(),
  signInWithRedirect: vi.fn(),
  signOut: vi.fn(),
}));

beforeEach(() => {
  vi.resetModules();
  vi.clearAllMocks();
  firebaseMocks.isFirebaseConfigured.mockReturnValue(true);
});

describe('resolveFirebaseAuth', () => {
  it('returns the configured Auth instance without changing its identity', async () => {
    const auth = { currentUser: null };
    firebaseMocks.getFirebaseAuth.mockReturnValue(auth);
    const { resolveFirebaseAuth } = await import('./AuthProvider');

    expect(resolveFirebaseAuth()).toEqual({ auth, error: null });
  });

  it('fails closed when Firebase app initialization throws', async () => {
    firebaseMocks.getFirebaseAuth.mockImplementation(() => {
      throw new Error('Firebase default app configuration does not match VITE_FIREBASE_* settings.');
    });
    const { resolveFirebaseAuth } = await import('./AuthProvider');

    expect(resolveFirebaseAuth()).toEqual({
      auth: null,
      error: 'Konfigurasi Firebase tidak cocok atau gagal diinisialisasi. Autentikasi dinonaktifkan.',
    });
  });

  it('preserves an unconfigured result without manufacturing an initialization error', async () => {
    firebaseMocks.getFirebaseAuth.mockReturnValue(null);
    const { resolveFirebaseAuth } = await import('./AuthProvider');

    expect(resolveFirebaseAuth()).toEqual({ auth: null, error: null });
  });
});

describe('subscribeToFirebaseAuth', () => {
  it('forwards signed-out and signed-in observer events and preserves cleanup', async () => {
    const { subscribeToFirebaseAuth } = await import('./AuthProvider');
    const auth = {} as Auth;
    const signedInUser = { uid: 'test-user' } as User;
    const onUser = vi.fn();
    const onError = vi.fn();
    const unsubscribe = vi.fn();
    firebaseMocks.onIdTokenChanged.mockReturnValue(unsubscribe);

    const cleanup = subscribeToFirebaseAuth(auth, { onUser, onError });
    const [observedAuth, nextUser, observerError] = firebaseMocks.onIdTokenChanged.mock.calls[0];

    expect(observedAuth).toBe(auth);
    expect(typeof nextUser).toBe('function');
    expect(typeof observerError).toBe('function');
    nextUser(null);
    nextUser(signedInUser);
    expect(onUser).toHaveBeenNthCalledWith(1, null);
    expect(onUser).toHaveBeenNthCalledWith(2, signedInUser);
    expect(onError).not.toHaveBeenCalled();
    cleanup?.();
    expect(unsubscribe).toHaveBeenCalledOnce();
  });

  it('subscribes to ID-token changes so refreshed credentials update the user observer', async () => {
    const { subscribeToFirebaseAuth } = await import('./AuthProvider');
    const initialUser = { uid: 'test-user', getIdToken: vi.fn().mockResolvedValue('old-token') } as unknown as User;
    const refreshedUser = { uid: 'test-user', getIdToken: vi.fn().mockResolvedValue('new-token') } as unknown as User;
    const onUser = vi.fn();
    const onError = vi.fn();
    firebaseMocks.onIdTokenChanged.mockReturnValue(vi.fn());

    subscribeToFirebaseAuth({} as Auth, { onUser, onError });
    const [observedAuth, nextUser, observerError] = firebaseMocks.onIdTokenChanged.mock.calls[0];

    expect(observedAuth).toBeDefined();
    expect(typeof nextUser).toBe('function');
    expect(typeof observerError).toBe('function');
    nextUser(initialUser);
    nextUser(refreshedUser);

    expect(onUser).toHaveBeenNthCalledWith(1, initialUser);
    expect(onUser).toHaveBeenNthCalledWith(2, refreshedUser);
    await expect(refreshedUser.getIdToken()).resolves.toBe('new-token');
    expect(onError).not.toHaveBeenCalled();
  });

  it('forwards asynchronous observer errors', async () => {
    const { subscribeToFirebaseAuth } = await import('./AuthProvider');
    const onUser = vi.fn();
    const onError = vi.fn();
    firebaseMocks.onIdTokenChanged.mockReturnValue(vi.fn());

    subscribeToFirebaseAuth({} as Auth, { onUser, onError });
    const observerError = firebaseMocks.onIdTokenChanged.mock.calls[0][2];
    const failure = { code: 'auth/network-request-failed' };
    observerError(failure);

    expect(onError).toHaveBeenCalledWith(failure);
  });

  it('fails closed when observer registration throws synchronously', async () => {
    const { subscribeToFirebaseAuth } = await import('./AuthProvider');
    const onUser = vi.fn();
    const onError = vi.fn();
    const failure = new Error('observer registration failed');
    firebaseMocks.onIdTokenChanged.mockImplementation(() => {
      throw failure;
    });

    const cleanup = subscribeToFirebaseAuth({} as Auth, { onUser, onError });

    expect(cleanup).toBeNull();
    expect(onError).toHaveBeenCalledWith(failure);
  });
});


describe('AuthProvider server-rendered context contract', () => {
  async function renderContext() {
    // Server rendering validates the context contract without pretending to
    // exercise browser effects, DOM mounting, or observer cleanup.
    const React = await import('react');
    const { renderToStaticMarkup } = await import('react-dom/server');
    const { AuthProvider, useAuth } = await import('./AuthProvider');
    let context: ReturnType<typeof useAuth> | null = null;
    function Probe() {
      context = useAuth();
      return React.createElement('span', null, context.status);
    }
    const html = renderToStaticMarkup(
      React.createElement(AuthProvider, null, React.createElement(Probe)),
    );
    return { context, html };
  }

  it('exposes the loading state while configured Firebase observer setup has not run', async () => {
    firebaseMocks.isFirebaseConfigured.mockReturnValue(true);
    const { context, html } = await renderContext();

    expect(html).toContain('loading');
    expect(context?.status).toBe('loading');
    expect(typeof context?.signInEmail).toBe('function');
    expect(typeof context?.registerEmail).toBe('function');
    expect(typeof context?.signInGoogle).toBe('function');
    expect(typeof context?.signOutUser).toBe('function');
    expect(typeof context?.getIdToken).toBe('function');
  });

  it('exposes an explicit unconfigured state instead of a fabricated signed-out state', async () => {
    firebaseMocks.isFirebaseConfigured.mockReturnValue(false);
    const { context, html } = await renderContext();

    expect(html).toContain('unconfigured');
    expect(context?.status).toBe('unconfigured');
    expect(context?.user).toBeNull();
  });

  it('rejects useAuth outside the provider boundary', async () => {
    const React = await import('react');
    const { renderToStaticMarkup } = await import('react-dom/server');
    const { useAuth } = await import('./AuthProvider');
    function Probe() {
      useAuth();
      return null;
    }

    expect(() => renderToStaticMarkup(React.createElement(Probe))).toThrow(
      'useAuth must be used inside AuthProvider.',
    );
  });
});
