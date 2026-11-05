# DEZZTA CHART

React + TypeScript + Vite chart application.

## Frontend environment

Copy `.env.example` to `.env.local` for local development. Configure these values in the frontend hosting provider (for example, Vercel) as build-time environment variables:

- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_APP_ID`
- `VITE_MARKET_DATA_API_BASE_URL`

Firebase web configuration is client configuration, not a Firebase Admin service-account credential. Never put a service-account JSON, private key, Databento API key, or backend secret in a `VITE_*` variable.

In Firebase Console, enable the Google and Email/Password providers and add the deployed frontend hostname to Authentication → Settings → Authorized domains. Google sign-in uses redirect flow for better compatibility with mobile browsers.

The Settings screen exposes Firebase sign-in and account creation. An authenticated Firebase user receives an ID token for the OHLCV HTTP request. Backend authorization and instrument entitlements remain mandatory; a successful login does not grant exchange-data access by itself.

## Market-data security

The market-data API must verify Firebase ID tokens server-side and enforce account/contract entitlements. Configure backend Firebase Admin credentials using the hosting platform's secret manager or workload identity. Never commit service-account credentials or provider API keys.

The chart continues to label its local fixture as DEMO. A backend response is not proof of live exchange data unless its feed state and provider provenance validate it.
