import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { Auth, User } from 'firebase/auth';

const firebaseMocks = vi.hoisted(() => ({
  getFirebaseAuth: vi.fn(),
  isFirebaseConfigured: vi.fn(),
  onAuthStateChanged: vi.fn(),
}));

vi.mock('../services/firebase', () => ({
  getFirebaseAuth: firebaseMocks.getFirebaseAuth,
  isFirebaseConfigured: firebaseMocks.isFirebaseConfigured,
  createGoogleProvider: vi.fn(),
}));

vi.mock('firebase/auth', () => ({
  createUserWithEmailAndPassword: vi.fn(),
  onAuthStateChanged: firebaseMocks.onAuthStateChanged,
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
    firebaseMocks.onAuthStateChanged.mockReturnValue(unsubscribe);

    const cleanup = subscribeToFirebaseAuth(auth, { onUser, onError });
    const [observedAuth, nextUser, observerError] = firebaseMocks.onAuthStateChanged.mock.calls[0];

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

  it('forwards asynchronous observer errors', async () => {
    const { subscribeToFirebaseAuth } = await import('./AuthProvider');
    const onUser = vi.fn();
    const onError = vi.fn();
    firebaseMocks.onAuthStateChanged.mockReturnValue(vi.fn());

    subscribeToFirebaseAuth({} as Auth, { onUser, onError });
    const observerError = firebaseMocks.onAuthStateChanged.mock.calls[0][2];
    const failure = { code: 'auth/network-request-failed' };
    observerError(failure);

    expect(onError).toHaveBeenCalledWith(failure);
  });

  it('fails closed when observer registration throws synchronously', async () => {
    const { subscribeToFirebaseAuth } = await import('./AuthProvider');
    const onUser = vi.fn();
    const onError = vi.fn();
    const failure = new Error('observer registration failed');
    firebaseMocks.onAuthStateChanged.mockImplementation(() => {
      throw failure;
    });

    const cleanup = subscribeToFirebaseAuth({} as Auth, { onUser, onError });

    expect(cleanup).toBeNull();
    expect(onError).toHaveBeenCalledWith(failure);
  });
});
