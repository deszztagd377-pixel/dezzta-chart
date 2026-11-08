import { getApps, initializeApp } from 'firebase/app';
import {
  getAuth,
  GoogleAuthProvider,
  type Auth,
} from 'firebase/auth';

function readFirebaseConfig() {
  const config = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
  };
  return Object.values(config).every((value) => typeof value === 'string' && value.trim())
    ? config
    : null;
}

let authInstance: Auth | null = null;

export function getFirebaseAuth(): Auth | null {
  if (authInstance) return authInstance;
  const config = readFirebaseConfig();
  if (!config) return null;

  // A named Firebase app may exist without a default app. Never infer that
  // getApps().length > 0 means the default app is available.
  const defaultApp = getApps().find((candidate) => candidate.name === '[DEFAULT]');
  const app = defaultApp ?? initializeApp(config);

  // Reusing a default app from another Firebase project would authenticate
  // against an unintended identity boundary. Fail closed on config mismatch.
  const configKeys: (keyof typeof config)[] = ['apiKey', 'authDomain', 'projectId', 'appId'];
  if (configKeys.some((key) => app.options[key] !== config[key])) {
    throw new Error('Firebase default app configuration does not match VITE_FIREBASE_* settings.');
  }

  authInstance = getAuth(app);
  return authInstance;
}

export function createGoogleProvider(): GoogleAuthProvider {
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: 'select_account' });
  return provider;
}

export function isFirebaseConfigured(): boolean {
  return readFirebaseConfig() !== null;
}
