import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  fetchInstrumentCatalog,
  InstrumentCatalogError,
  parseInstrumentCatalog,
} from './instrumentCatalogClient';

const contract = {
  root: 'ES',
  product_name: 'E-mini S&P 500 Futures',
  dataset: 'GLBX.MDP3',
  raw_symbol: 'ESZ6',
  instrument_id: 123,
  publisher_id: 1,
  instrument_class: 'F',
  expiration: '2026-12-18',
  currency: 'USD',
  min_price_increment: '0.25',
  definition_ts_event_ns: '1793577600000000000',
  provider: 'databento',
  series_type: 'contract',
};

const catalog = (overrides: Record<string, unknown> = {}) => ({
  dataset: 'GLBX.MDP3',
  state: 'ready',
  supported_products: [
    { root: 'ES', product_name: 'E-mini S&P 500 Futures' },
    { root: 'NQ', product_name: 'E-mini Nasdaq-100 Futures' },
    { root: 'GC', product_name: 'Gold Futures' },
  ],
  contract_count: 1,
  contracts: [{ ...contract }],
  selection_policy: 'No contract is auto-selected.',
  requested_root: 'ES',
  ...overrides,
});

const response = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

const options = (fetchImpl: typeof fetch, overrides: Record<string, unknown> = {}) => ({
  baseUrl: 'https://market.example.test/api/',
  root: 'ES' as const,
  fetchImpl,
  ...overrides,
});

afterEach(() => vi.useRealTimers());

describe('parseInstrumentCatalog', () => {
  it('accepts a valid provider-backed contract without changing its identifiers', () => {
    const result = parseInstrumentCatalog(catalog());
    expect(result.contracts[0].raw_symbol).toBe('ESZ6');
    expect(result.contracts[0].instrument_id).toBe(123);
    expect(result.contracts[0].min_price_increment).toBe('0.25');
  });

  it('accepts an honest empty catalog state', () => {
    const result = parseInstrumentCatalog(catalog({
      state: 'definitions_unavailable',
      contract_count: 0,
      contracts: [],
    }));
    expect(result.contracts).toEqual([]);
    expect(result.state).toBe('definitions_unavailable');
  });

  it('rejects count and state mismatches', () => {
    expect(() => parseInstrumentCatalog(catalog({ contract_count: 2 }))).toThrow(/contract_count/);
    expect(() => parseInstrumentCatalog(catalog({ state: 'definitions_unavailable' }))).toThrow(/state/);
  });

  it('accepts an empty root-filtered result when the global catalog is ready', () => {
    const result = parseInstrumentCatalog(catalog({
      state: 'ready',
      contract_count: 0,
      contracts: [],
    }));
    expect(result.state).toBe('ready');
    expect(result.contracts).toEqual([]);
  });

  it('rejects impossible calendar dates', () => {
    expect(() => parseInstrumentCatalog(catalog({
      contracts: [{ ...contract, expiration: '2026-02-31' }],
    }))).toThrow(/metadata/);
  });

  it('rejects symbols that do not match their declared product root', () => {
    expect(() => parseInstrumentCatalog(catalog({
      contracts: [{ ...contract, raw_symbol: 'NQZ6' }],
    }))).toThrow(/raw symbol/);
  });

  it('rejects spreads and non-outright contract classes', () => {
    expect(() => parseInstrumentCatalog(catalog({
      contracts: [{ ...contract, instrument_class: 'S' }],
    }))).toThrow(/metadata/);
  });

  it('rejects duplicate contract identities', () => {
    expect(() => parseInstrumentCatalog(catalog({
      contract_count: 2,
      contracts: [{ ...contract }, { ...contract, raw_symbol: 'ESH7' }],
    }))).toThrow(/duplicate contract identities/);
  });

  it('rejects contracts returned outside the requested root', () => {
    expect(() => parseInstrumentCatalog(catalog({
      contracts: [{ ...contract, root: 'NQ', raw_symbol: 'NQZ6' }],
    }))).toThrow(/outside the requested root/);
  });

  it('rejects non-decimal tick sizes and invalid expiration dates', () => {
    expect(() => parseInstrumentCatalog(catalog({
      contracts: [{ ...contract, min_price_increment: '0.25x' }],
    }))).toThrow(/metadata/);
    expect(() => parseInstrumentCatalog(catalog({
      contracts: [{ ...contract, expiration: 'not-a-date' }],
    }))).toThrow(/metadata/);
  });
});

describe('fetchInstrumentCatalog', () => {
  it('requests the selected product root from the existing endpoint', async () => {
    const fetchImpl = vi.fn<typeof fetch>().mockResolvedValue(response(catalog()));
    await fetchInstrumentCatalog(options(fetchImpl));
    const [requestUrl, init] = fetchImpl.mock.calls[0];
    const url = new URL(String(requestUrl));
    expect(url.pathname).toBe('/api/v1/instruments');
    expect(url.searchParams.get('root')).toBe('ES');
    expect(init?.method).toBe('GET');
    expect(init?.cache).toBe('no-store');
  });

  it('classifies HTTP and invalid JSON responses', async () => {
    await expect(fetchInstrumentCatalog(options(
      vi.fn<typeof fetch>().mockResolvedValue(new Response('no', { status: 503 })),
    ))).rejects.toMatchObject({ code: 'http', statusCode: 503 });
    await expect(fetchInstrumentCatalog(options(
      vi.fn<typeof fetch>().mockResolvedValue(new Response('{bad', { status: 200 })),
    ))).rejects.toMatchObject({ code: 'invalid_json' });
  });

  it('classifies network errors', async () => {
    await expect(fetchInstrumentCatalog(options(
      vi.fn<typeof fetch>().mockRejectedValue(new Error('offline')),
    ))).rejects.toMatchObject({ code: 'network' });
  });

  it('supports cancellation and does not start an already-cancelled request', async () => {
    const controller = new AbortController();
    const fetchImpl = vi.fn<typeof fetch>((_input, init) => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    }));
    const pending = fetchInstrumentCatalog(options(fetchImpl, { signal: controller.signal }));
    controller.abort();
    await expect(pending).rejects.toMatchObject({ code: 'cancelled' });

    const alreadyCancelled = new AbortController();
    alreadyCancelled.abort();
    const neverFetch = vi.fn<typeof fetch>();
    await expect(fetchInstrumentCatalog(options(neverFetch, { signal: alreadyCancelled.signal })))
      .rejects.toBeInstanceOf(InstrumentCatalogError);
    expect(neverFetch).not.toHaveBeenCalled();
  });

  it('enforces timeout and invalid configuration', async () => {
    vi.useFakeTimers();
    const fetchImpl = vi.fn<typeof fetch>((_input, init) => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    }));
    const pending = fetchInstrumentCatalog(options(fetchImpl, { timeoutMs: 40 }));
    const rejection = expect(pending).rejects.toMatchObject({ code: 'timeout' });
    await vi.advanceTimersByTimeAsync(40);
    await rejection;

    await expect(fetchInstrumentCatalog(options(fetchImpl, { baseUrl: '' })))
      .rejects.toMatchObject({ code: 'configuration' });
  });
});
