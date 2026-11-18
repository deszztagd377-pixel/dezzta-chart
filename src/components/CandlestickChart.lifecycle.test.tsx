// @vitest-environment jsdom

import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { FuturesContractDto } from '../types/instrumentCatalogApi';

const mocks = vi.hoisted(() => ({
  createChart: vi.fn(),
  startSupervisor: vi.fn(),
  getIdToken: vi.fn(async () => 'fresh-firebase-token'),
  user: { uid: 'lifecycle-test-user' },
}));

vi.mock('../auth/AuthProvider', () => ({
  useAuth: () => ({ user: mocks.user, getIdToken: mocks.getIdToken }),
}));

vi.mock('lightweight-charts', () => ({
  createChart: mocks.createChart,
  CandlestickSeries: {},
}));

vi.mock('../services/ohlcvStreamSupervisor', () => ({
  startOhlcvStreamSupervisor: mocks.startSupervisor,
}));

import CandlestickChart from './CandlestickChart';
import { getMarketDataSnapshot } from '../services/marketDataStore';

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

function renderChart() {
  if (!root) throw new Error('React root is not initialized.');
  act(() => {
    root?.render(
      <CandlestickChart
        timeframe="1m"
        showGrid
        selectedContract={selectedContract}
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
  setBrowserLifecycle(true, 'visible');
  stopHandles = [];
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);

  chartApi = {
    addSeries: vi.fn(() => ({
      setData: vi.fn(),
      update: vi.fn(),
    })),
    timeScale: vi.fn(() => ({
      fitContent: vi.fn(),
      applyOptions: vi.fn(),
    })),
    applyOptions: vi.fn(),
    resize: vi.fn(),
    remove: vi.fn(),
  };
  mocks.createChart.mockReturnValue(chartApi);
  mocks.startSupervisor.mockImplementation(() => {
    const stop = vi.fn();
    stopHandles.push(stop);
    return { stop, status: 'connecting' };
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
  it('stops offline, recreates on return online, pauses hidden, and cleans up on unmount', () => {
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

    renderChart();
    expect(mocks.startSupervisor).toHaveBeenCalledTimes(1);
    expect(stopHandles).toHaveLength(1);

    setBrowserLifecycle(false, 'visible');
    act(() => window.dispatchEvent(new Event('offline')));
    expect(stopHandles[0]).toHaveBeenCalledOnce();
    expect(getMarketDataSnapshot().status).toBe('unavailable');
    expect(getMarketDataSnapshot().detail).toContain('offline');

    setBrowserLifecycle(true, 'visible');
    act(() => window.dispatchEvent(new Event('online')));
    expect(mocks.startSupervisor).toHaveBeenCalledTimes(2);

    setBrowserLifecycle(true, 'hidden');
    act(() => document.dispatchEvent(new Event('visibilitychange')));
    expect(stopHandles[1]).toHaveBeenCalledOnce();
    expect(getMarketDataSnapshot().status).toBe('unavailable');
    expect(getMarketDataSnapshot().detail).toContain('background');

    setBrowserLifecycle(true, 'visible');
    act(() => document.dispatchEvent(new Event('visibilitychange')));
    expect(mocks.startSupervisor).toHaveBeenCalledTimes(3);

    act(() => {
      root?.unmount();
      root = null;
    });
    expect(stopHandles[2]).toHaveBeenCalledOnce();
  });

  it('does not create a supervisor when initially offline', () => {
    setBrowserLifecycle(false, 'visible');
    renderChart();
    expect(mocks.startSupervisor).not.toHaveBeenCalled();

    setBrowserLifecycle(true, 'visible');
    act(() => window.dispatchEvent(new Event('online')));
    expect(mocks.startSupervisor).toHaveBeenCalledTimes(1);
  });

  it('does not create a supervisor when initially hidden', () => {
    setBrowserLifecycle(true, 'hidden');
    renderChart();
    expect(mocks.startSupervisor).not.toHaveBeenCalled();

    setBrowserLifecycle(true, 'visible');
    act(() => document.dispatchEvent(new Event('visibilitychange')));
    expect(mocks.startSupervisor).toHaveBeenCalledTimes(1);
  });
});
