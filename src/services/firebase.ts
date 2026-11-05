import { getApp, getApps, initializeApp } from 'firebase/app';
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
  const app = getApps().length > 0 ? getApp() : initializeApp(config);
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
