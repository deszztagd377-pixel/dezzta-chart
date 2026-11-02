/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_MARKET_DATA_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
