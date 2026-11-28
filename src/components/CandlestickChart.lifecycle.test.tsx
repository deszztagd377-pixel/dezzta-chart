// @vitest-environment jsdom

import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { Timeframe } from '../types';
import type { FuturesContractDto } from '../types/instrumentCatalogApi';
import type { MarketSeriesIdentity } from '../services/marketDataStore';

const mocks = vi.hoisted(() => ({
  createChart: vi.fn(),
  acquireSupervisor: vi.fn(),
  getIdToken: vi.fn(async () => 'fresh-firebase-token'),
  user: { uid: 'lifecycle-test-user' },
}));

vi.mock('../auth/AuthProvider', () => ({
  useAuth: () => ({ user: mocks.user, getIdToken: mocks.getIdToken }),
}));

vi.mock('lightweight-charts', () => ({
  createChart: mocks.createChart,
  CandlestickSeries: {},
  LineSeries: {},
}));

vi.mock('../services/ohlcvSeriesSupervisorRegistry', () => ({
  ohlcvSeriesSupervisorRegistry: { acquire: mocks.acquireSupervisor },
}));

import CandlestickChart from './CandlestickChart';
import { marketDataSeriesStore } from '../services/marketDataSeriesStore';
import { getBucketIdentityForTimeframe } from '../utils/ohlcvBucketPolicy';

const selectedContract: FuturesContractDto = {
  root: 'ES',
  product_name: 'E-mini S&P 500',
  dataset: 'GLBX.MDP3',
  raw_symbol: 'ESH7',
  instrument_id: 12345,
  publisher_id: 1,
  instrument_class: 'F',
  expiration: '2027-03-19',
  currency: 'USD',
  min_price_increment: '0.25',
  definition_ts_event_ns: '1790000000000000000',
  provider: 'databento',
  series_type: 'contract',
  canonical_instrument_id: '11111111-1111-4111-8111-111111111111',
};
const marketDataIdentity = {
  dataset: selectedContract.dataset,
  publisherId: selectedContract.publisher_id,
  instrumentId: selectedContract.instrument_id,
  rawSymbol: selectedContract.raw_symbol,
  timeframe: '1m' as const,
  ...getBucketIdentityForTimeframe('1m'),
};


let container: HTMLDivElement;
let root: Root | null;
let stopHandles: ReturnType<typeof vi.fn>[];
let chartApi: {
  addSeries: ReturnType<typeof vi.fn>;
  timeScale: ReturnType<typeof vi.fn>;
  applyOptions: ReturnType<typeof vi.fn>;
  resize: ReturnType<typeof vi.fn>;
  remove: ReturnType<typeof vi.fn>;
};
let chartSeries: Array<{
  setData: ReturnType<typeof vi.fn>;
  update: ReturnType<typeof vi.fn>;
}>;

function setBrowserLifecycle(online: boolean, visibility: DocumentVisibilityState) {
  Object.defineProperty(navigator, 'onLine', {
    configurable: true,
    value: online,
  });
  Object.defineProperty(document, 'visibilityState', {
    configurable: true,
    value: visibility,
  });
}

function renderChart(
  contract: FuturesContractDto = selectedContract,
  timeframe: Timeframe = '1m',
) {
  if (!root) throw new Error('React root is not initialized.');
  act(() => {
    root?.render(
      <CandlestickChart
        timeframe={timeframe}
        showGrid
        selectedContract={contract}
        marketDataApiBaseUrl="https://market-data.example.test"
      />,
    );
  });
}

beforeEach(() => {
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean })
    .IS_REACT_ACT_ENVIRONMENT = true;
  vi.resetAllMocks();
  vi.stubGlobal('ResizeObserver', undefined as unknown as typeof ResizeObserver);
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
    width: 800,
    height: 420,
    top: 0,
    left: 0,
    right: 800,
    bottom: 420,
    x: 0,
    y: 0,
    toJSON: () => ({}),
  } as DOMRect);
  setBrowserLifecycle(true, 'visible');
  stopHandles = [];
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);

  chartSeries = [];
  chartApi = {
    addSeries: vi.fn(() => {
      const series = { setData: vi.fn(), update: vi.fn() };
      chartSeries.push(series);
      return series;
    }),
    timeScale: vi.fn(() => ({
      fitContent: vi.fn(),
      applyOptions: vi.fn(),
    })),
    applyOptions: vi.fn(),
    resize: vi.fn(),
    remove: vi.fn(),
  };
  mocks.createChart.mockReturnValue(chartApi);
  mocks.acquireSupervisor.mockImplementation((options: { identity: MarketSeriesIdentity }) => {
    const release = vi.fn(() => marketDataSeriesStore.reset(options.identity, 'unavailable', 'Stream paused by browser lifecycle.'));
    stopHandles.push(release);
    marketDataSeriesStore.reset(options.identity, 'loading', 'Connecting in lifecycle test.');
    return { release, key: 'lifecycle-test', ownerId: 'panel-test', generation: stopHandles.length };
  });
});

afterEach(() => {
  if (root) {
    act(() => root?.unmount());
    root = null;
  }
  container.remove();
  setBrowserLifecycle(true, 'visible');
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  (globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean })
    .IS_REACT_ACT_ENVIRONMENT = false;
});

describe('CandlestickChart WebSocket browser lifecycle integration', () => {
  it('creates the SMA, EMA and Bollinger overlay series with the candlestick chart', () => {
    renderChart();
    expect(chartApi.addSeries).toHaveBeenCalledTimes(6);
  });

  it('renders finite indicator values from the selected backend snapshot', () => {
    renderChart();
    const bars = Array.from({ length: 25 }, (_, index) => ({
      timestamp: 1_800_000_000 + index * 60,
      open: 100 + index,
      high: 102 + index,
      low: 99 + index,
      close: 100 + index,
      volume: 10 + index,
    }));

    act(() => marketDataSeriesStore.publishSnapshot({
      identity: marketDataIdentity,
      status: 'ready',
      bars,
    }));

    expect(chartSeries).toHaveLength(6);
    const overlayData = chartSeries.slice(1).map((series) => {
      const calls = series.setData.mock.calls;
      return calls[calls.length - 1]?.[0] as Array<{ time: number; value: number }>;
    });
    expect(overlayData).toHaveLength(5);
    for (const points of overlayData) {
      expect(points).toHaveLength(6);
      expect(points.every((point) => Number.isFinite(point.value))).toBe(true);
    }
    expect(overlayData[0][0].time).toBe(bars[19].timestamp);
    expect(overlayData[0][5].value).toBeCloseTo(114.5, 10);
    expect(overlayData[1][5].value).toBeCloseTo(114.5, 10);
    expect(overlayData[2][5].value).toBeCloseTo(114.5, 10);
  });

  it('uses a loaded CME calendar release only for daily-or-higher chart series', () => {
    const cmeContract: FuturesContractDto = {
      ...selectedContract,
      session_calendar_id: 'CME_EQUITY_INDEX',
      session_calendar_version: 'test-only-2024.01',
    };
    renderChart(cmeContract, '1d');

    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(1);
    expect(mocks.acquireSupervisor.mock.calls[0][0].identity).toMatchObject({
      timeframe: '1d',
      bucketPolicy: 'CME_SESSION_V1',
      calendarId: 'CME_EQUITY_INDEX',
      calendarVersion: 'test-only-2024.01',
    });
  });

  it('does not enable CME session buckets until a calendar release version is loaded', () => {
    const pendingCalendarContract: FuturesContractDto = {
      ...selectedContract,
      session_calendar_id: 'CME_EQUITY_INDEX',
      session_calendar_version: null,
    };
    renderChart(pendingCalendarContract, '1d');

    expect(mocks.acquireSupervisor.mock.calls[0][0].identity).toMatchObject({
      timeframe: '1d',
      bucketPolicy: 'UTC_LEGACY',
      calendarId: '',
      calendarVersion: '',
    });
  });
  it('stops offline, recreates on return online, pauses hidden, and cleans up on unmount', () => {
    renderChart();
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(1);
    expect(stopHandles).toHaveLength(1);

    setBrowserLifecycle(false, 'visible');
    act(() => window.dispatchEvent(new Event('offline')));
    expect(stopHandles[0]).toHaveBeenCalledOnce();
    expect(marketDataSeriesStore.getSnapshot(marketDataIdentity).status).toBe('unavailable');
    expect(marketDataSeriesStore.getSnapshot(marketDataIdentity).detail).toContain('offline');

    setBrowserLifecycle(true, 'visible');
    act(() => window.dispatchEvent(new Event('online')));
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(2);

    setBrowserLifecycle(true, 'hidden');
    act(() => document.dispatchEvent(new Event('visibilitychange')));
    expect(stopHandles[1]).toHaveBeenCalledOnce();
    expect(marketDataSeriesStore.getSnapshot(marketDataIdentity).status).toBe('unavailable');
    expect(marketDataSeriesStore.getSnapshot(marketDataIdentity).detail).toContain('background');

    setBrowserLifecycle(true, 'visible');
    act(() => document.dispatchEvent(new Event('visibilitychange')));
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(3);

    act(() => {
      root?.unmount();
      root = null;
    });
    expect(stopHandles[2]).toHaveBeenCalledOnce();
  });

  it('does not create a supervisor when initially offline', () => {
    setBrowserLifecycle(false, 'visible');
    renderChart();
    expect(mocks.acquireSupervisor).not.toHaveBeenCalled();

    setBrowserLifecycle(true, 'visible');
    act(() => window.dispatchEvent(new Event('online')));
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(1);
  });

  it('coalesces rapid offline, hidden and return events without overlapping supervisors', () => {
    renderChart();
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(1);

    setBrowserLifecycle(false, 'visible');
    act(() => window.dispatchEvent(new Event('offline')));
    expect(stopHandles[0]).toHaveBeenCalledOnce();

    setBrowserLifecycle(false, 'hidden');
    act(() => document.dispatchEvent(new Event('visibilitychange')));
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(1);

    setBrowserLifecycle(true, 'hidden');
    act(() => window.dispatchEvent(new Event('online')));
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(1);

    setBrowserLifecycle(true, 'visible');
    act(() => document.dispatchEvent(new Event('visibilitychange')));
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(2);

    act(() => window.dispatchEvent(new Event('online')));
    act(() => document.dispatchEvent(new Event('visibilitychange')));
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(2);
    expect(stopHandles[1]).not.toHaveBeenCalled();

    act(() => {
      root?.unmount();
      root = null;
    });
    expect(stopHandles[1]).toHaveBeenCalledOnce();
  });

  it('pauses on pagehide and creates a fresh supervisor on pageshow', () => {
    renderChart();
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(1);

    act(() => window.dispatchEvent(new Event('pagehide')));
    expect(stopHandles[0]).toHaveBeenCalledOnce();
    expect(marketDataSeriesStore.getSnapshot(marketDataIdentity).status).toBe('unavailable');
    expect(marketDataSeriesStore.getSnapshot(marketDataIdentity).detail).toContain('background');

    setBrowserLifecycle(true, 'visible');
    act(() => window.dispatchEvent(new Event('pageshow')));
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(2);
    expect(stopHandles[1]).not.toHaveBeenCalled();

    act(() => {
      root?.unmount();
      root = null;
    });
    expect(stopHandles[1]).toHaveBeenCalledOnce();
  });

  it('does not create a supervisor when initially hidden', () => {
    setBrowserLifecycle(true, 'hidden');
    renderChart();
    expect(mocks.acquireSupervisor).not.toHaveBeenCalled();

    setBrowserLifecycle(true, 'visible');
    act(() => document.dispatchEvent(new Event('visibilitychange')));
    expect(mocks.acquireSupervisor).toHaveBeenCalledTimes(1);
  });
});
