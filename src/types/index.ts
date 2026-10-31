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

export type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w' | '1M';

export type ChartType = 'candlestick' | 'line' | 'bar' | 'area';

export type Theme = 'dark' | 'light';

export interface UserPreferences {
  theme: Theme;
  chartType: ChartType;
  timeframe: Timeframe;
}