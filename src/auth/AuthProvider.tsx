import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  createUserWithEmailAndPassword,
  onIdTokenChanged,
  signInWithEmailAndPassword,
  signInWithRedirect,
  signOut,
  type Auth,
  type User,
} from 'firebase/auth';
import { createGoogleProvider, getFirebaseAuth, isFirebaseConfigured } from '../services/firebase';

type AuthStatus = 'unconfigured' | 'loading' | 'signed-out' | 'signed-in' | 'error';

interface AuthContextValue {
  user: User | null;
  status: AuthStatus;
  error: string | null;
  signInEmail(email: string, password: string): Promise<void>;
  registerEmail(email: string, password: string): Promise<void>;
  signInGoogle(): Promise<void>;
  signOutUser(): Promise<void>;
  getIdToken(): Promise<string>;
  clearError(): void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function readableAuthError(error: unknown): string {
  const code = typeof error === 'object' && error !== null && 'code' in error
    ? String((error as { code: unknown }).code)
    : '';
  const messages: Record<string, string> = {
    'auth/invalid-email': 'Format email tidak valid.',
    'auth/user-disabled': 'Akun ini dinonaktifkan.',
    'auth/user-not-found': 'Akun tidak ditemukan.',
    'auth/wrong-password': 'Email atau password tidak cocok.',
    'auth/invalid-credential': 'Email atau password tidak cocok.',
    'auth/email-already-in-use': 'Email sudah digunakan.',
    'auth/weak-password': 'Password terlalu lemah. Gunakan minimal 6 karakter.',
    'auth/network-request-failed': 'Koneksi jaringan bermasalah.',
    'auth/too-many-requests': 'Terlalu banyak percobaan. Coba lagi nanti.',
    'auth/unauthorized-domain': 'Domain aplikasi belum diizinkan di Firebase Authentication.',
  };
  return messages[code] ?? 'Autentikasi gagal. Periksa konfigurasi Firebase dan coba lagi.';
}

export type FirebaseAuthResolution =
  | { auth: Auth; error: null }
  | { auth: null; error: string | null };

export interface FirebaseAuthObserverHandlers {
  onUser(user: User | null): void;
  onError(error: unknown): void;
}

/**
 * Keep observer setup behind a fail-closed boundary. Firebase can reject
 * subscription synchronously; observer errors are forwarded to the same
 * handler and cleanup is preserved.
 */
export function subscribeToFirebaseAuth(
  auth: Auth,
  handlers: FirebaseAuthObserverHandlers,
): (() => void) | null {
  try {
    return onIdTokenChanged(auth, handlers.onUser, handlers.onError);
  } catch (error) {
    handlers.onError(error);
    return null;
  }
}

/**
 * Firebase initialization can throw when an existing default app belongs to
 * another project. Convert that boundary failure into an explicit auth state
 * instead of allowing a React effect or user action to throw uncaught.
 */
export function resolveFirebaseAuth(): FirebaseAuthResolution {
  try {
    return { auth: getFirebaseAuth(), error: null };
  } catch {
    return {
      auth: null,
      error: 'Konfigurasi Firebase tidak cocok atau gagal diinisialisasi. Autentikasi dinonaktifkan.',
    };
  }
}

export interface FirebaseAuthLifecycleHandlers {
  onUser(user: User | null): void;
  onStatus(status: AuthStatus): void;
  onError(message: string): void;
}

/**
 * Own the complete auth-observer boundary used by the React effect.
 * Cleanup first deactivates callbacks, then unsubscribes, so a queued
 * observer callback cannot publish stale state after teardown.
 */
export function startFirebaseAuthObserver(
  handlers: FirebaseAuthLifecycleHandlers,
): (() => void) | null {
  const resolution = resolveFirebaseAuth();
  if (resolution.error) {
    handlers.onError(resolution.error);
    handlers.onStatus('error');
    return null;
  }
  if (!resolution.auth) return null;

  let active = true;
  const unsubscribe = subscribeToFirebaseAuth(resolution.auth, {
    onUser: (nextUser) => {
      if (!active) return;
      handlers.onUser(nextUser);
      handlers.onStatus(nextUser ? 'signed-in' : 'signed-out');
    },
    onError: (reason) => {
      if (!active) return;
      handlers.onUser(null);
      handlers.onError(readableAuthError(reason));
      handlers.onStatus('error');
    },
  });

  return () => {
    if (!active) return;
    active = false;
    unsubscribe?.();
  };
}

export const AuthProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<AuthStatus>(
    isFirebaseConfigured() ? 'loading' : 'unconfigured',
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => startFirebaseAuthObserver({
    onUser: setUser,
    onStatus: setStatus,
    onError: setError,
  }), []);

  const runAuthAction = useCallback(async (action: (auth: Auth) => Promise<unknown>) => {
    const resolution = resolveFirebaseAuth();
    if (resolution.error) {
      setError(resolution.error);
      setStatus('error');
      return;
    }
    if (!resolution.auth) {
      setError('Firebase belum dikonfigurasi. Lengkapi environment VITE_FIREBASE_* terlebih dahulu.');
      setStatus('unconfigured');
      return;
    }
    setError(null);
    try {
      await action(resolution.auth);
    } catch (reason) {
      setError(readableAuthError(reason));
      setStatus('error');
    }
  }, []);

  const signInEmail = useCallback((email: string, password: string) =>
    runAuthAction((auth) => signInWithEmailAndPassword(auth, email.trim(), password)), [runAuthAction]);
  const registerEmail = useCallback((email: string, password: string) =>
    runAuthAction((auth) => createUserWithEmailAndPassword(auth, email.trim(), password)), [runAuthAction]);
  const signInGoogle = useCallback(() =>
    runAuthAction((auth) => signInWithRedirect(auth, createGoogleProvider())), [runAuthAction]);
  const signOutUser = useCallback(() => runAuthAction((auth) => signOut(auth)), [runAuthAction]);
  const getIdToken = useCallback(async () => {
    const resolution = resolveFirebaseAuth();
    if (resolution.error) throw new Error(resolution.error);
    if (!resolution.auth?.currentUser) throw new Error('Pengguna belum login ke Firebase.');
    return resolution.auth.currentUser.getIdToken();
  }, []);
  const clearError = useCallback(() => setError(null), []);

  const value = useMemo(() => ({
    user, status, error, signInEmail, registerEmail, signInGoogle, signOutUser, getIdToken, clearError,
  }), [user, status, error, signInEmail, registerEmail, signInGoogle, signOutUser, getIdToken, clearError]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider.');
  return context;
}
