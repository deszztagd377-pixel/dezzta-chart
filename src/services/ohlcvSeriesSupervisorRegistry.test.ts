import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { marketDataSeriesStore } from './marketDataSeriesStore';
import { OhlcvSeriesSupervisorRegistry } from './ohlcvSeriesSupervisorRegistry';

class FakeSocket {
  readyState = 0;
  sent: string[] = [];
  listeners = new Map<string, Array<(event: Event) => void>>();

  addEventListener(type: string, listener: EventListenerOrEventListenerObject) {
    const callback = typeof listener === 'function'
      ? listener as (event: Event) => void
      : (event: Event) => listener.handleEvent(event);
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), callback]);
  }
  send(value: string) { this.sent.push(value); }
  close(code = 1000, reason = '') {
    this.readyState = 3;
    this.emit('close', Object.assign(new Event('close'), { code, reason }));
  }
  emit(type: string, event: Event) {
    for (const listener of this.listeners.get(type) ?? []) listener(event);
  }
  message(value: unknown) {
    this.emit('message', new MessageEvent('message', { data: JSON.stringify(value) }));
  }
}

const es = {
  provider: 'databento',
  seriesType: 'contract' as const,
  dataset: 'GLBX.MDP3',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'ESZ6',
  timeframe: '1s' as const,
};
const nq = { ...es, instrumentId: 456, rawSymbol: 'NQZ6' };
const makeSnapshot = (identity: typeof es, streamId: string) => ({
  type: 'market_data.ohlcv.snapshot',
  version: 1,
  state: 'ready',
  feedState: 'live',
  timestampUnit: 'nanoseconds',
  priceRepresentation: 'decimal-string',
  count: 1,
  truncated: false,
  bars: [{
    dataset: identity.dataset,
    provider: identity.provider,
    publisherId: identity.publisherId,
    instrumentId: identity.instrumentId,
    rawSymbol: identity.rawSymbol,
    seriesType: identity.seriesType,
    timeframe: identity.timeframe,
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
  }],
  detail: null,
  streamId,
  watermark: 7,
  cursor: '100',
});

const makeOptions = (identity: typeof es, socket: FakeSocket, onStatus?: (status: string) => void) => ({
  baseUrl: 'https://market.example.test',
  identity,
  canonicalInstrumentId: identity.instrumentId === 123
    ? '11111111-1111-4111-8111-111111111111'
    : '22222222-2222-4222-8222-222222222222',
  getIdToken: async () => 'fresh-id-token',
  webSocketFactory: () => socket as unknown as WebSocket,
  requestWebSocketTicket: async () => 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
  random: () => 0,
  onStatus: onStatus as ((status: 'connecting' | 'authenticated' | 'subscribed' | 'reconnecting' | 'stopped') => void) | undefined,
});

async function authenticateAndPublish(socket: FakeSocket, identity: typeof es, streamId: string) {
  await vi.waitFor(() => expect(socket.listeners.has('open')).toBe(true));
  socket.readyState = 1;
  socket.emit('open', new Event('open'));
  socket.message({ type: 'market_data.status', version: 1 });
  socket.message(makeSnapshot(identity, streamId));
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async () => ({
    ok: true,
    status: 200,
    json: async () => ({
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      expiresIn: 90,
      purpose: 'market-data',
    }),
  }) as unknown as Response));
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  marketDataSeriesStore.reset(es, 'unavailable', 'test reset');
  marketDataSeriesStore.reset(nq, 'unavailable', 'test reset');
});

describe('per-series shared OHLCV supervisor registry', () => {
  it('runs different canonical series concurrently without cross-writing either snapshot', async () => {
    const registry = new OhlcvSeriesSupervisorRegistry();
    const esSocket = new FakeSocket();
    const nqSocket = new FakeSocket();
    const esLease = registry.acquire(makeOptions(es, esSocket), 'panel-es');
    const nqLease = registry.acquire(makeOptions(nq, nqSocket), 'panel-nq');

    expect(registry.getSeriesCount()).toBe(2);
    expect(registry.getOwnerCount(es)).toBe(1);
    expect(registry.getOwnerCount(nq)).toBe(1);
    await Promise.all([
      authenticateAndPublish(esSocket, es, 'stream-es'),
      authenticateAndPublish(nqSocket, nq, 'stream-nq'),
    ]);

    expect(marketDataSeriesStore.getSnapshot(es).bars[0].close).toBe(6000.75);
    expect(marketDataSeriesStore.getSnapshot(nq).bars[0].close).toBe(6000.75);
    expect(marketDataSeriesStore.getSnapshot(es).identity?.rawSymbol).toBe('ESZ6');
    expect(marketDataSeriesStore.getSnapshot(nq).identity?.rawSymbol).toBe('NQZ6');

    esLease.release();
    expect(registry.getSeriesCount()).toBe(1);
    expect(marketDataSeriesStore.getSnapshot(nq).source).toBe('backend');
    nqLease.release();
    expect(registry.getSeriesCount()).toBe(0);
    expect(marketDataSeriesStore.getSnapshot(nq).status).toBe('unavailable');
  });

  it('shares one socket for two panels on the same series and closes only after final release', async () => {
    const registry = new OhlcvSeriesSupervisorRegistry();
    const socket = new FakeSocket();
    const statusesA: string[] = [];
    const statusesB: string[] = [];
    const first = registry.acquire(makeOptions(es, socket, (status) => statusesA.push(status)), 'panel-a');

    expect(registry.getSeriesCount()).toBe(1);
    await authenticateAndPublish(socket, es, 'stream-shared');
    expect(statusesA).toContain('subscribed');

    // A late-joining panel reuses the active transport and receives its current state.
    const unusedSocket = new FakeSocket();
    const second = registry.acquire(makeOptions(es, unusedSocket, (status) => statusesB.push(status)), 'panel-b');
    expect(registry.getOwnerCount(es)).toBe(2);
    expect(statusesB).toEqual(['subscribed']);
    expect(unusedSocket.listeners.size).toBe(0);

    first.release();
    expect(registry.getOwnerCount(es)).toBe(1);
    expect(socket.readyState).toBe(1);
    expect(marketDataSeriesStore.getSnapshot(es).source).toBe('backend');

    second.release();
    expect(registry.getSeriesCount()).toBe(0);
    expect(socket.readyState).toBe(3);
    expect(marketDataSeriesStore.getSnapshot(es).status).toBe('unavailable');
  });

  it('rejects conflicting endpoint or canonical mapping for an already-owned series', () => {
    const registry = new OhlcvSeriesSupervisorRegistry();
    const socket = new FakeSocket();
    const first = registry.acquire(makeOptions(es, socket), 'panel-a');

    expect(() => registry.acquire({
      ...makeOptions(es, new FakeSocket()),
      canonicalInstrumentId: '33333333-3333-4333-8333-333333333333',
    }, 'panel-b')).toThrow(/different transport endpoint or canonical instrument mapping/);

    expect(() => registry.acquire({
      ...makeOptions(es, new FakeSocket()),
      baseUrl: 'https://other-market.example.test',
    }, 'panel-c')).toThrow(/different transport endpoint or canonical instrument mapping/);

    expect(registry.getSeriesCount()).toBe(1);
    expect(registry.getOwnerCount(es)).toBe(1);
    expect(socket.readyState).toBe(0);
    first.release();
    expect(registry.getSeriesCount()).toBe(0);
  });

  it('bounds concurrent canonical series and leaves existing owners intact at capacity', () => {
    const registry = new OhlcvSeriesSupervisorRegistry(1);
    const first = registry.acquire(makeOptions(es, new FakeSocket()), 'panel-es');

    expect(registry.getCapacity()).toBe(1);
    expect(registry.getSeriesCount()).toBe(1);
    expect(() => registry.acquire(makeOptions(nq, new FakeSocket()), 'panel-nq'))
      .toThrow(/capacity \(1\) is exhausted/);
    expect(registry.getOwnerCount(es)).toBe(1);
    expect(registry.getSeriesCount()).toBe(1);

    first.release();
    expect(registry.getSeriesCount()).toBe(0);
  });

  it('rejects invalid active-series capacities', () => {
    expect(() => new OhlcvSeriesSupervisorRegistry(0)).toThrow(/positive safe integer/);
    expect(() => new OhlcvSeriesSupervisorRegistry(1.5)).toThrow(/positive safe integer/);
  });

  it('ignores stale panel cleanup after the same owner reacquires the series', () => {
    const registry = new OhlcvSeriesSupervisorRegistry();
    const socket = new FakeSocket();
    const stale = registry.acquire(makeOptions(es, socket), 'panel-a');
    const current = registry.acquire(makeOptions(es, socket), 'panel-a');

    expect(registry.getOwnerCount(es)).toBe(1);
    stale.release();
    expect(registry.getOwnerCount(es)).toBe(1);
    expect(registry.getSeriesCount()).toBe(1);
    current.release();
    expect(registry.getSeriesCount()).toBe(0);
  });
});
