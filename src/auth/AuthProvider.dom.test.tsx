// @vitest-environment jsdom

import React, { StrictMode, act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { Auth, User } from 'firebase/auth';

const firebaseMocks = vi.hoisted(() => ({
  getFirebaseAuth: vi.fn(),
  isFirebaseConfigured: vi.fn(),
  onIdTokenChanged: vi.fn(),
  createUserWithEmailAndPassword: vi.fn(),
  signInWithEmailAndPassword: vi.fn(),
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

import { AuthProvider, useAuth } from './AuthProvider';

type Observer = {
  onUser: (user: User | null) => void;
  onError: (error: unknown) => void;
  unsubscribe: ReturnType<typeof vi.fn>;
};

let container: HTMLDivElement;
let root: Root | null;
let observers: Observer[];

function Probe() {
  const { user, status, error } = useAuth();
  return (
    <section>
      <output data-testid="status">{status}</output>
      <output data-testid="user">{user?.uid ?? 'none'}</output>
      <output data-testid="error">{error ?? ''}</output>
    </section>
  );
}

function renderProvider(children: React.ReactNode = <Probe />) {
  if (!root) throw new Error('React root is not initialized.');
  act(() => {
    root?.render(<AuthProvider>{children}</AuthProvider>);
  });
}

function read(testId: string): string {
  const element = container.querySelector(`[data-testid="${testId}"]`);
  return element?.textContent ?? '';
}

beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean })
    .IS_REACT_ACT_ENVIRONMENT = true;
  vi.resetAllMocks();
  observers = [];
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);

  firebaseMocks.isFirebaseConfigured.mockReturnValue(true);
  firebaseMocks.getFirebaseAuth.mockReturnValue({ currentUser: null } as Auth);
  firebaseMocks.onIdTokenChanged.mockImplementation(
    (_auth: Auth, onUser: Observer['onUser'], onError: Observer['onError']) => {
      const observer: Observer = {
        onUser,
        onError,
        unsubscribe: vi.fn(),
      };
      observers.push(observer);
      return observer.unsubscribe;
    },
  );
});

afterEach(() => {
  if (root) {
    act(() => root?.unmount());
    root = null;
  }
  container.remove();
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean })
    .IS_REACT_ACT_ENVIRONMENT = false;
});

describe('AuthProvider React DOM lifecycle', () => {
  it('mounts, publishes signed-out and signed-in transitions, and renders the current user', () => {
    renderProvider();
    expect(read('status')).toBe('loading');
    expect(observers).toHaveLength(1);

    act(() => observers[0].onUser(null));
    expect(read('status')).toBe('signed-out');
    expect(read('user')).toBe('none');

    const user = { uid: 'dom-user' } as User;
    act(() => observers[0].onUser(user));
    expect(read('status')).toBe('signed-in');
    expect(read('user')).toBe('dom-user');
  });

  it('renders a safe error state when the Firebase observer reports an error', () => {
    renderProvider();

    act(() => observers[0].onError({ code: 'auth/network-request-failed' }));

    expect(read('status')).toBe('error');
    expect(read('user')).toBe('none');
    expect(read('error')).toBe('Koneksi jaringan bermasalah.');
  });

  it('unsubscribes on unmount and ignores callbacks queued after cleanup', () => {
    renderProvider();
    const lateCallback = observers[0].onUser;

    act(() => {
      root?.unmount();
      root = null;
    });

    expect(observers[0].unsubscribe).toHaveBeenCalledOnce();
    act(() => lateCallback({ uid: 'late-user' } as User));
    expect(container.innerHTML).toBe('');
  });

  it('keeps the first StrictMode effect subscription inert after its cleanup', () => {
    if (!root) throw new Error('React root is not initialized.');
    act(() => {
      root?.render(<StrictMode><AuthProvider><Probe /></AuthProvider></StrictMode>);
    });

    expect(observers).toHaveLength(2);
    expect(observers[0].unsubscribe).toHaveBeenCalledOnce();

    act(() => observers[0].onUser({ uid: 'stale-user' } as User));
    expect(read('status')).toBe('loading');
    expect(read('user')).toBe('none');

    act(() => observers[1].onUser({ uid: 'current-user' } as User));
    expect(read('status')).toBe('signed-in');
    expect(read('user')).toBe('current-user');
  });

  it('fails closed in the mounted provider when Firebase initialization throws', () => {
    firebaseMocks.getFirebaseAuth.mockImplementation(() => {
      throw new Error('private Firebase project details');
    });

    renderProvider();

    expect(read('status')).toBe('error');
    expect(read('error')).toBe(
      'Konfigurasi Firebase tidak cocok atau gagal diinisialisasi. Autentikasi dinonaktifkan.',
    );
    expect(firebaseMocks.onIdTokenChanged).not.toHaveBeenCalled();
  });

  it('keeps the provider explicitly unconfigured without subscribing to Firebase', () => {
    firebaseMocks.isFirebaseConfigured.mockReturnValue(false);
    firebaseMocks.getFirebaseAuth.mockReturnValue(null);

    renderProvider();

    expect(read('status')).toBe('unconfigured');
    expect(read('error')).toBe('');
    expect(firebaseMocks.onIdTokenChanged).not.toHaveBeenCalled();
  });

  it('renders a safe error state when observer registration throws synchronously', () => {
    firebaseMocks.onIdTokenChanged.mockImplementation(() => {
      throw { code: 'auth/network-request-failed' };
    });

    renderProvider();

    expect(read('status')).toBe('error');
    expect(read('error')).toBe('Koneksi jaringan bermasalah.');
  });
});
