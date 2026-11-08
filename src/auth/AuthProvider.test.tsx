import { beforeEach, describe, expect, it, vi } from 'vitest';

const firebaseMocks = vi.hoisted(() => ({
  getFirebaseAuth: vi.fn(),
  isFirebaseConfigured: vi.fn(),
}));

vi.mock('../services/firebase', () => ({
  getFirebaseAuth: firebaseMocks.getFirebaseAuth,
  isFirebaseConfigured: firebaseMocks.isFirebaseConfigured,
  createGoogleProvider: vi.fn(),
}));

vi.mock('firebase/auth', () => ({
  createUserWithEmailAndPassword: vi.fn(),
  onAuthStateChanged: vi.fn(),
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
