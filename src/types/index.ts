
// Type definitions for DEZZTA CHART application

export interface SymbolData {
  id: string;
  name: string;
  symbol: string;
  exchange: string;
}

export interface ChartData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// Supported chart timeframes
export type Timeframe =
  | '1s'
  | '5s'
  | '15s'
  | '30s'
  | '45s'
  | '1m'
  | '3m'
  | '5m'
  | '15m'
  | '30m'
  | '45m'
  | '1h'
  | '2h'
  | '4h'
  | '1d'
  | '1w'
  | '1M'
  | '3M';

// Supported chart styles
export type ChartType =
  | 'candlestick'
  | 'line'
  | 'bar'
  | 'area';

export type Theme = 'dark' | 'light';

export interface UserPreferences {
  theme: Theme;
  chartType: ChartType;
  timeframe: Timeframe;
}
