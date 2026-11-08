import { beforeEach, describe, expect, it, vi } from 'vitest';

const firebaseMocks = vi.hoisted(() => ({
  getApps: vi.fn(),
  initializeApp: vi.fn(),
  getAuth: vi.fn(),
  setGoogleCustomParameters: vi.fn(),
}));

vi.mock('firebase/app', () => ({
  getApps: firebaseMocks.getApps,
  initializeApp: firebaseMocks.initializeApp,
}));

vi.mock('firebase/auth', () => ({
  getAuth: firebaseMocks.getAuth,
  GoogleAuthProvider: class {
    setCustomParameters(parameters: Record<string, string>) {
      firebaseMocks.setGoogleCustomParameters(parameters);
    }
  },
}));

const config = {
  apiKey: 'test-api-key',
  authDomain: 'dezzta-test.firebaseapp.com',
  projectId: 'dezzta-test-project',
  appId: '1:123456789:web:test-app',
};

const defaultApp = {
  name: '[DEFAULT]',
  options: { ...config },
};
const auth = { name: 'mock-auth' };

function stubFirebaseEnvironment(overrides: Partial<typeof config> = {}) {
  const values = { ...config, ...overrides };
  vi.stubEnv('VITE_FIREBASE_API_KEY', values.apiKey);
  vi.stubEnv('VITE_FIREBASE_AUTH_DOMAIN', values.authDomain);
  vi.stubEnv('VITE_FIREBASE_PROJECT_ID', values.projectId);
  vi.stubEnv('VITE_FIREBASE_APP_ID', values.appId);
}

beforeEach(() => {
  vi.resetModules();
  vi.unstubAllEnvs();
  vi.clearAllMocks();
  stubFirebaseEnvironment();
  firebaseMocks.getApps.mockReturnValue([]);
  firebaseMocks.initializeApp.mockReturnValue(defaultApp);
  firebaseMocks.getAuth.mockReturnValue(auth);
});

describe('Firebase client configuration', () => {
  it('fails closed when any required environment value is missing', async () => {
    vi.stubEnv('VITE_FIREBASE_PROJECT_ID', '');
    const service = await import('./firebase');

    expect(service.isFirebaseConfigured()).toBe(false);
    expect(service.getFirebaseAuth()).toBeNull();
    expect(firebaseMocks.initializeApp).not.toHaveBeenCalled();
    expect(firebaseMocks.getAuth).not.toHaveBeenCalled();
  });

  it('initializes the default app once and memoizes its Auth instance', async () => {
    const service = await import('./firebase');

    expect(service.isFirebaseConfigured()).toBe(true);
    expect(service.getFirebaseAuth()).toBe(auth);
    expect(service.getFirebaseAuth()).toBe(auth);
    expect(firebaseMocks.initializeApp).toHaveBeenCalledOnce();
    expect(firebaseMocks.initializeApp).toHaveBeenCalledWith(config);
    expect(firebaseMocks.getAuth).toHaveBeenCalledOnce();
    expect(firebaseMocks.getAuth).toHaveBeenCalledWith(defaultApp);
  });

  it('does not mistake a named app for the default app', async () => {
    firebaseMocks.getApps.mockReturnValue([{ name: 'secondary', options: config }]);
    const service = await import('./firebase');

    expect(service.getFirebaseAuth()).toBe(auth);
    expect(firebaseMocks.initializeApp).toHaveBeenCalledWith(config);
    expect(firebaseMocks.getAuth).toHaveBeenCalledWith(defaultApp);
  });

  it('reuses a matching default app when named apps also exist', async () => {
    const existingDefault = { ...defaultApp };
    firebaseMocks.getApps.mockReturnValue([
      { name: 'secondary', options: config },
      existingDefault,
    ]);
    const service = await import('./firebase');

    expect(service.getFirebaseAuth()).toBe(auth);
    expect(firebaseMocks.initializeApp).not.toHaveBeenCalled();
    expect(firebaseMocks.getAuth).toHaveBeenCalledWith(existingDefault);
  });

  it('rejects a pre-existing default app from a different Firebase project', async () => {
    firebaseMocks.getApps.mockReturnValue([{
      name: '[DEFAULT]',
      options: { ...config, projectId: 'unexpected-project' },
    }]);
    const service = await import('./firebase');

    expect(() => service.getFirebaseAuth()).toThrow(/does not match/);
    expect(firebaseMocks.getAuth).not.toHaveBeenCalled();
  });

  it('configures Google sign-in to request explicit account selection', async () => {
    const service = await import('./firebase');

    service.createGoogleProvider();

    expect(firebaseMocks.setGoogleCustomParameters).toHaveBeenCalledWith({
      prompt: 'select_account',
    });
  });
});
