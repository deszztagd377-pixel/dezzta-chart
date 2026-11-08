import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { Auth, User } from 'firebase/auth';

const firebaseMocks = vi.hoisted(() => ({
  getFirebaseAuth: vi.fn(),
  isFirebaseConfigured: vi.fn(),
  onIdTokenChanged: vi.fn(),
  signInWithEmailAndPassword: vi.fn(),
  createUserWithEmailAndPassword: vi.fn(),
  signInWithRedirect: vi.fn(),
  signOut: vi.fn(),
  createGoogleProvider: vi.fn(),
}));

vi.mock('../services/firebase', () => ({
  getFirebaseAuth: firebaseMocks.getFirebaseAuth,
  isFirebaseConfigured: firebaseMocks.isFirebaseConfigured,
  createGoogleProvider: firebaseMocks.createGoogleProvider,
}));

vi.mock('firebase/auth', () => ({
  createUserWithEmailAndPassword: firebaseMocks.createUserWithEmailAndPassword,
  onIdTokenChanged: firebaseMocks.onIdTokenChanged,
  signInWithEmailAndPassword: firebaseMocks.signInWithEmailAndPassword,
  signInWithRedirect: firebaseMocks.signInWithRedirect,
  signOut: firebaseMocks.signOut,
}));

beforeEach(() => {
  vi.resetModules();
  vi.clearAllMocks();
  firebaseMocks.isFirebaseConfigured.mockReturnValue(true);
});

describe('readableAuthError', () => {
  it('maps known Firebase error codes to safe user-facing messages', async () => {
    const { readableAuthError } = await import('./AuthProvider');

    expect(readableAuthError({ code: 'auth/invalid-email', message: 'raw provider detail' }))
      .toBe('Format email tidak valid.');
    expect(readableAuthError({ code: 'auth/too-many-requests', message: 'raw provider detail' }))
      .toBe('Terlalu banyak percobaan. Coba lagi nanti.');
  });

  it('does not expose unknown provider messages or token-like error details', async () => {
    const { readableAuthError } = await import('./AuthProvider');
    const sensitiveMessage = 'permission denied for project secret-project; token=private-value';

    expect(readableAuthError(new Error(sensitiveMessage)))
      .toBe('Autentikasi gagal. Periksa konfigurasi Firebase dan coba lagi.');
    expect(readableAuthError({ code: 'auth/unrecognized', message: sensitiveMessage }))
      .not.toContain('private-value');
    expect(readableAuthError(null))
      .toBe('Autentikasi gagal. Periksa konfigurasi Firebase dan coba lagi.');
  });
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


describe('startFirebaseAuthObserver lifecycle boundary', () => {
  function handlers() {
    return {
      onUser: vi.fn(),
      onStatus: vi.fn(),
      onError: vi.fn(),
    };
  }

  it('maps signed-out, signed-in, and observer-error events into auth state', async () => {
    const auth = { currentUser: null } as Auth;
    const unsubscribe = vi.fn();
    firebaseMocks.getFirebaseAuth.mockReturnValue(auth);
    firebaseMocks.onIdTokenChanged.mockReturnValue(unsubscribe);
    const { startFirebaseAuthObserver } = await import('./AuthProvider');
    const callbacks = handlers();

    const cleanup = startFirebaseAuthObserver(callbacks);
    const [observedAuth, nextUser, observerError] = firebaseMocks.onIdTokenChanged.mock.calls[0];
    const signedInUser = { uid: 'lifecycle-user' } as User;

    expect(observedAuth).toBe(auth);
    nextUser(null);
    nextUser(signedInUser);
    observerError({ code: 'auth/network-request-failed' });

    expect(callbacks.onUser).toHaveBeenNthCalledWith(1, null);
    expect(callbacks.onUser).toHaveBeenNthCalledWith(2, signedInUser);
    expect(callbacks.onUser).toHaveBeenNthCalledWith(3, null);
    expect(callbacks.onStatus.mock.calls).toEqual([
      ['signed-out'],
      ['signed-in'],
      ['error'],
    ]);
    expect(callbacks.onError).toHaveBeenCalledWith('Koneksi jaringan bermasalah.');
    cleanup?.();
    expect(unsubscribe).toHaveBeenCalledOnce();
  });

  it('ignores queued observer callbacks after cleanup and unsubscribes only once', async () => {
    const auth = { currentUser: null } as Auth;
    const unsubscribe = vi.fn();
    firebaseMocks.getFirebaseAuth.mockReturnValue(auth);
    firebaseMocks.onIdTokenChanged.mockReturnValue(unsubscribe);
    const { startFirebaseAuthObserver } = await import('./AuthProvider');
    const callbacks = handlers();

    const cleanup = startFirebaseAuthObserver(callbacks);
    const [, nextUser, observerError] = firebaseMocks.onIdTokenChanged.mock.calls[0];
    cleanup?.();
    cleanup?.();

    nextUser({ uid: 'late-user' } as User);
    observerError({ code: 'auth/network-request-failed' });

    expect(unsubscribe).toHaveBeenCalledOnce();
    expect(callbacks.onUser).not.toHaveBeenCalled();
    expect(callbacks.onStatus).not.toHaveBeenCalled();
    expect(callbacks.onError).not.toHaveBeenCalled();
  });

  it('fails closed when Firebase initialization fails', async () => {
    firebaseMocks.getFirebaseAuth.mockImplementation(() => {
      throw new Error('default app mismatch');
    });
    const { startFirebaseAuthObserver } = await import('./AuthProvider');
    const callbacks = handlers();

    expect(startFirebaseAuthObserver(callbacks)).toBeNull();
    expect(callbacks.onError).toHaveBeenCalledWith(
      'Konfigurasi Firebase tidak cocok atau gagal diinisialisasi. Autentikasi dinonaktifkan.',
    );
    expect(callbacks.onStatus).toHaveBeenCalledWith('error');
    expect(firebaseMocks.onIdTokenChanged).not.toHaveBeenCalled();
  });

  it('does not manufacture a signed-out state when Firebase is unconfigured', async () => {
    firebaseMocks.isFirebaseConfigured.mockReturnValue(false);
    firebaseMocks.getFirebaseAuth.mockReturnValue(null);
    const { startFirebaseAuthObserver } = await import('./AuthProvider');
    const callbacks = handlers();

    expect(startFirebaseAuthObserver(callbacks)).toBeNull();
    expect(callbacks.onUser).not.toHaveBeenCalled();
    expect(callbacks.onStatus).not.toHaveBeenCalled();
    expect(callbacks.onError).not.toHaveBeenCalled();
    expect(firebaseMocks.onIdTokenChanged).not.toHaveBeenCalled();
  });

  it('reports synchronous observer-registration failure as a safe error state', async () => {
    firebaseMocks.getFirebaseAuth.mockReturnValue({ currentUser: null });
    firebaseMocks.onIdTokenChanged.mockImplementation(() => {
      throw { code: 'auth/network-request-failed' };
    });
    const { startFirebaseAuthObserver } = await import('./AuthProvider');
    const callbacks = handlers();

    const cleanup = startFirebaseAuthObserver(callbacks);

    expect(cleanup).toBeTypeOf('function');
    expect(callbacks.onError).toHaveBeenCalledWith('Koneksi jaringan bermasalah.');
    expect(callbacks.onStatus).toHaveBeenCalledWith('error');
    cleanup?.();
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


describe('AuthProvider Firebase action contract', () => {
  async function renderActionContext() {
    // Server rendering exposes the provider's action callbacks without
    // claiming to exercise useEffect, browser DOM mounting, or cleanup.
    const React = await import('react');
    const { renderToStaticMarkup } = await import('react-dom/server');
    const { AuthProvider, useAuth } = await import('./AuthProvider');
    let context: ReturnType<typeof useAuth> | null = null;
    function Probe() {
      context = useAuth();
      return null;
    }
    renderToStaticMarkup(
      React.createElement(AuthProvider, null, React.createElement(Probe)),
    );
    if (!context) throw new Error('AuthProvider context was not captured.');
    return context;
  }

  it('trims email before calling Firebase email sign-in', async () => {
    const auth = { currentUser: null } as Auth;
    firebaseMocks.getFirebaseAuth.mockReturnValue(auth);
    firebaseMocks.signInWithEmailAndPassword.mockResolvedValue({});
    const context = await renderActionContext();

    await context.signInEmail('  student@example.test  ', 'test-password');

    expect(firebaseMocks.signInWithEmailAndPassword)
      .toHaveBeenCalledWith(auth, 'student@example.test', 'test-password');
  });

  it('trims email before calling Firebase account registration', async () => {
    const auth = { currentUser: null } as Auth;
    firebaseMocks.getFirebaseAuth.mockReturnValue(auth);
    firebaseMocks.createUserWithEmailAndPassword.mockResolvedValue({});
    const context = await renderActionContext();

    await context.registerEmail('  student@example.test  ', 'test-password');

    expect(firebaseMocks.createUserWithEmailAndPassword)
      .toHaveBeenCalledWith(auth, 'student@example.test', 'test-password');
  });

  it('uses the resolved Firebase Auth instance for Google redirect', async () => {
    const auth = { currentUser: null } as Auth;
    const provider = { providerId: 'google.com' };
    firebaseMocks.getFirebaseAuth.mockReturnValue(auth);
    firebaseMocks.createGoogleProvider.mockReturnValue(provider);
    firebaseMocks.signInWithRedirect.mockResolvedValue({});
    const context = await renderActionContext();

    await context.signInGoogle();

    expect(firebaseMocks.createGoogleProvider).toHaveBeenCalledOnce();
    expect(firebaseMocks.signInWithRedirect).toHaveBeenCalledWith(auth, provider);
  });

  it('uses the resolved Firebase Auth instance for sign-out', async () => {
    const auth = { currentUser: null } as Auth;
    firebaseMocks.getFirebaseAuth.mockReturnValue(auth);
    firebaseMocks.signOut.mockResolvedValue(undefined);
    const context = await renderActionContext();

    await context.signOutUser();

    expect(firebaseMocks.signOut).toHaveBeenCalledOnce();
    expect(firebaseMocks.signOut).toHaveBeenCalledWith(auth);
  });

  it('retrieves an ID token only from the current Firebase user', async () => {
    const getIdToken = vi.fn().mockResolvedValue('test-id-token');
    firebaseMocks.getFirebaseAuth.mockReturnValue({
      currentUser: { getIdToken },
    });
    const context = await renderActionContext();

    await expect(context.getIdToken()).resolves.toBe('test-id-token');
    expect(getIdToken).toHaveBeenCalledOnce();
  });

  it('rejects token retrieval when no Firebase user is signed in', async () => {
    firebaseMocks.getFirebaseAuth.mockReturnValue({ currentUser: null });
    const context = await renderActionContext();

    await expect(context.getIdToken()).rejects.toThrow(
      'Pengguna belum login ke Firebase.',
    );
  });
});
