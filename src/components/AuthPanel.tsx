import React, { useState } from 'react';
import { useAuth } from '../auth/AuthProvider';
import './AuthPanel.css';

const AuthPanel: React.FC = () => {
  const { user, status, error, signInEmail, registerEmail, signInGoogle, signOutUser, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);

  const perform = async (action: () => Promise<void>) => {
    setBusy(true);
    try { await action(); } finally { setBusy(false); }
  };

  return (
    <section className="auth-panel" aria-labelledby="auth-panel-title">
      <div className="auth-panel__heading">
        <div>
          <p className="auth-panel__eyebrow">ACCOUNT SECURITY</p>
          <h3 id="auth-panel-title">Firebase account</h3>
        </div>
        <span className={status === 'signed-in' ? 'auth-panel__state is-online' : 'auth-panel__state'}>
          {status === 'signed-in' ? 'SIGNED IN' : status === 'loading' ? 'CHECKING' : status === 'unconfigured' ? 'NOT CONFIGURED' : 'SIGNED OUT'}
        </span>
      </div>

      {user ? (
        <div className="auth-panel__signed-in">
          <strong>{user.displayName || user.email || 'Authenticated user'}</strong>
          <small>{user.email ?? 'Google account'}</small>
          <button type="button" disabled={busy} onClick={() => void perform(signOutUser)}>
            {busy ? 'Please wait…' : 'Sign out'}
          </button>
        </div>
      ) : (
        <>
          <button className="auth-panel__google" type="button" disabled={busy || status === 'unconfigured'} onClick={() => void perform(signInGoogle)}>
            Continue with Google
          </button>
          <div className="auth-panel__separator"><span>OR USE EMAIL</span></div>
          <label>Email
            <input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@example.com" />
          </label>
          <label>Password
            <input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Minimum 6 characters" />
          </label>
          <div className="auth-panel__actions">
            <button type="button" disabled={busy || status === 'unconfigured' || !email.trim() || !password} onClick={() => void perform(() => signInEmail(email, password))}>Sign in</button>
            <button type="button" className="is-secondary" disabled={busy || status === 'unconfigured' || !email.trim() || password.length < 6} onClick={() => void perform(() => registerEmail(email, password))}>Create account</button>
          </div>
        </>
      )}

      {status === 'unconfigured' && <p className="auth-panel__hint">Firebase Console sudah disiapkan, tetapi environment VITE_FIREBASE_* belum tersedia di aplikasi.</p>}
      {error && <p className="auth-panel__error" role="alert">{error} <button type="button" onClick={clearError}>Dismiss</button></p>}
      <p className="auth-panel__hint">Login hanya membuktikan identitas akun. Akses data pasar tetap memerlukan entitlement backend yang valid.</p>
    </section>
  );
};

export default AuthPanel;
