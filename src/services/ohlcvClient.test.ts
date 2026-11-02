import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchOhlcvSnapshot, OhlcvRequestError } from './ohlcvClient';

const identity = {
  dataset: 'GLBX.MDP3',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'ESZ6',
  timeframe: '1s' as const,
};

const bar = {
  dataset: 'GLBX.MDP3',
  provider: 'databento',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'ESZ6',
  seriesType: 'contract',
  timeframe: '1s',
  tsStartNs: '1793577600000000000',
  open: '6000.125',
  high: '6001.250',
  low: '5999.875',
  close: '6000.750',
  volume: '12',
  tsEventNs: '1793577600999000000',
  tsReceivedNs: '1793577601000000000',
  sequence: 7,
  sequenceOrigin: 'local',
  origin: 'provider',
  completeness: 'complete',
};

const snapshot = (overrides: Record<string, unknown> = {}) => ({
  type: 'market_data.ohlcv.snapshot',
  version: 1,
  state: 'ready',
  feedState: 'live',
  timestampUnit: 'nanoseconds',
  priceRepresentation: 'decimal-string',
  count: 1,
  truncated: false,
  bars: [{ ...bar }],
  detail: null,
  ...overrides,
});

const jsonResponse = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });

const options = (fetchImpl: typeof fetch, overrides: Record<string, unknown> = {}) => ({
  baseUrl: 'https://market.example.test/api/',
  identity,
  fetchImpl,
  ...overrides,
});

afterEach(() => {
  vi.useRealTimers();
});

describe('fetchOhlcvSnapshot', () => {
  it('requests only the exact instrument and timeframe using backend query names', async () => {
    const fetchImpl = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(snapshot()));
    await fetchOhlcvSnapshot(options(fetchImpl, { limit: 250 }));

    const [requestUrl, init] = fetchImpl.mock.calls[0];
    const url = new URL(String(requestUrl));
    expect(url.pathname).toBe('/api/v1/ohlcv');
    expect(url.searchParams.get('dataset')).toBe('GLBX.MDP3');
    expect(url.searchParams.get('publisher_id')).toBe('1');
    expect(url.searchParams.get('instrument_id')).toBe('123');
    expect(url.searchParams.get('raw_symbol')).toBe('ESZ6');
    expect(url.searchParams.get('timeframe')).toBe('1s');
    expect(url.searchParams.get('limit')).toBe('250');
    expect(init?.method).toBe('GET');
    expect(init?.cache).toBe('no-store');
  });

  it('returns validated chart candles for an exact live series', async () => {
    const result = await fetchOhlcvSnapshot(options(
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(snapshot())),
    ));
    expect(result.status).toBe('ready');
    expect(result.candles).toHaveLength(1);
    expect(result.candles[0].open).toBe(6000.125);
  });

  it('does not treat a disconnected feed as confirmed live data', async () => {
    const result = await fetchOhlcvSnapshot(options(
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(snapshot({ feedState: 'disconnected' }))),
    ));
    expect(result.status).toBe('degraded');
    expect(result.candles).toHaveLength(1);
  });

  it('returns unavailable when the requested exact series has no bars', async () => {
    const result = await fetchOhlcvSnapshot(options(
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(snapshot({
        state: 'unavailable', bars: [], count: 0, feedState: 'disconnected',
      }))),
    ));
    expect(result.status).toBe('unavailable');
    expect(result.candles).toEqual([]);
  });

  it('returns unavailable rather than mixing another instrument', async () => {
    const result = await fetchOhlcvSnapshot(options(
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(snapshot({
        bars: [{ ...bar, instrumentId: 999 }],
      }))),
    ));
    expect(result.status).toBe('unavailable');
    expect(result.candles).toEqual([]);
  });

  it('rejects an invalid snapshot envelope', async () => {
    await expect(fetchOhlcvSnapshot(options(
      vi.fn<typeof fetch>().mockResolvedValue(jsonResponse({ version: 99 })),
    ))).rejects.toMatchObject({ code: 'invalid_snapshot' });
  });

  it('rejects non-success HTTP responses without parsing them as snapshots', async () => {
    await expect(fetchOhlcvSnapshot(options(
      vi.fn<typeof fetch>().mockResolvedValue(new Response('unavailable', { status: 503 })),
    ))).rejects.toMatchObject({ code: 'http', statusCode: 503 });
  });

  it('rejects invalid JSON', async () => {
    await expect(fetchOhlcvSnapshot(options(
      vi.fn<typeof fetch>().mockResolvedValue(new Response('{broken', { status: 200 })),
    ))).rejects.toMatchObject({ code: 'invalid_json' });
  });

  it('classifies network failures', async () => {
    await expect(fetchOhlcvSnapshot(options(
      vi.fn<typeof fetch>().mockRejectedValue(new Error('offline')),
    ))).rejects.toMatchObject({ code: 'network' });
  });

  it('supports caller cancellation', async () => {
    const controller = new AbortController();
    const fetchImpl = vi.fn<typeof fetch>((_input, init) => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    }));
    const pending = fetchOhlcvSnapshot(options(fetchImpl, { signal: controller.signal }));
    controller.abort();
    await expect(pending).rejects.toMatchObject({ code: 'cancelled' });
  });

  it('enforces the request timeout', async () => {
    vi.useFakeTimers();
    const fetchImpl = vi.fn<typeof fetch>((_input, init) => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    }));
    const pending = fetchOhlcvSnapshot(options(fetchImpl, { timeoutMs: 50 }));
    const rejection = expect(pending).rejects.toMatchObject({ code: 'timeout' });
    await vi.advanceTimersByTimeAsync(50);
    await rejection;
  });

  it('rejects an unverified or invalid base URL and unsafe limit', async () => {
    const fetchImpl = vi.fn<typeof fetch>();
    await expect(fetchOhlcvSnapshot(options(fetchImpl, { baseUrl: '' })))
      .rejects.toMatchObject({ code: 'configuration' });
    await expect(fetchOhlcvSnapshot(options(fetchImpl, { limit: 5001 })))
      .rejects.toMatchObject({ code: 'configuration' });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it('does not start a request when the caller already cancelled it', async () => {
    const controller = new AbortController();
    controller.abort();
    const fetchImpl = vi.fn<typeof fetch>();
    await expect(fetchOhlcvSnapshot(options(fetchImpl, { signal: controller.signal })))
      .rejects.toBeInstanceOf(OhlcvRequestError);
    expect(fetchImpl).not.toHaveBeenCalled();
  });
});
