import { afterEach, describe, expect, it, vi } from 'vitest';
import { getMarketDataSnapshot, resetMarketDataSnapshot } from './marketDataStore';
import { startOhlcvStreamSupervisor } from './ohlcvStreamSupervisor';

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
    this.emit('close', new CloseEvent('close', { code, reason }));
  }
  serverClose(code: number, reason = '') { this.close(code, reason); }
  emit(type: string, event: Event) {
    for (const listener of this.listeners.get(type) ?? []) listener(event);
  }
  message(value: unknown) {
    this.emit('message', new MessageEvent('message', { data: JSON.stringify(value) }));
  }
}

const identity = {
  dataset: 'GLBX.MDP3',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'ESZ6',
  timeframe: '1s' as const,
};
const bar = {
  dataset: 'GLBX.MDP3', provider: 'databento', publisherId: 1, instrumentId: 123,
  rawSymbol: 'ESZ6', seriesType: 'contract', timeframe: '1s',
  tsStartNs: '1793577600000000000', open: '6000.125', high: '6001.250',
  low: '5999.875', close: '6000.750', volume: '12',
  tsEventNs: '1793577600999000000', tsReceivedNs: '1793577601000000000',
  sequence: 7, sequenceOrigin: 'local', origin: 'provider', completeness: 'complete',
};
const snapshot = {
  type: 'market_data.ohlcv.snapshot', version: 1, state: 'ready', feedState: 'live',
  timestampUnit: 'nanoseconds', priceRepresentation: 'decimal-string',
  count: 1, truncated: false, bars: [bar], detail: null,
  streamId: 'stream-a', watermark: 7,
};

afterEach(() => {
  vi.useRealTimers();
  resetMarketDataSnapshot(null, 'demo', 'test reset');
});

describe('OHLCV stream supervisor', () => {
  it('requests an ID token and publishes the validated snapshot into the shared store', async () => {
    const socket = new FakeSocket();
    const getIdToken = vi.fn().mockResolvedValue('fresh-id-token');
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: 'canonical-esz6',
      getIdToken,
      webSocketFactory: () => socket as unknown as WebSocket,
      random: () => 0,
    });
    await vi.waitFor(() => expect(getIdToken).toHaveBeenCalledOnce());
    await vi.waitFor(() => expect(socket.listeners.has('open')).toBe(true));
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    expect(JSON.parse(socket.sent[0])).toEqual({ type: 'auth', token: 'fresh-id-token' });
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);

    expect(supervisor.status).toBe('subscribed');
    expect(getMarketDataSnapshot().source).toBe('backend');
    expect(getMarketDataSnapshot().bars).toHaveLength(1);
    supervisor.stop();
    expect(supervisor.status).toBe('stopped');
    expect(getMarketDataSnapshot().bars).toHaveLength(0);
  });

  it('uses bounded exponential reconnect and requests a fresh token for the next attempt', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    let tokenCount = 0;
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: 'canonical-esz6',
      getIdToken: async () => `token-${++tokenCount}`,
      webSocketFactory: () => {
        const socket = new FakeSocket();
        sockets.push(socket);
        return socket as unknown as WebSocket;
      },
      minReconnectDelayMs: 100,
      maxReconnectDelayMs: 400,
      random: () => 0,
    });
    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].readyState = 1;
    sockets[0].emit('open', new Event('open'));
    sockets[0].message({ type: 'market_data.status', version: 1 });
    sockets[0].message(snapshot);
    sockets[0].message({
      type: 'market_data.ohlcv.update', version: 1, streamId: 'stream-a',
      eventId: 'gap', sequence: 9, emittedAtNs: '1793577601000000000',
      operation: 'upsert', isFinal: true, series: identity,
      bar: { ...bar, sequence: 9 },
    });
    expect(supervisor.status).toBe('reconnecting');
    await vi.advanceTimersByTimeAsync(49);
    expect(sockets).toHaveLength(1);
    await vi.advanceTimersByTimeAsync(1);
    await vi.waitFor(() => expect(sockets).toHaveLength(2));
    expect(sockets).toHaveLength(2);
    expect(tokenCount).toBe(2);
    supervisor.stop();
  });

  it('does not retry after the server rejects authentication or entitlement', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const factory = vi.fn(() => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: 'canonical-esz6',
      getIdToken: async () => 'fresh-token',
      webSocketFactory: factory,
      minReconnectDelayMs: 10,
      random: () => 0,
    });
    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].serverClose(4403, 'Instrument access denied');
    expect(supervisor.status).toBe('stopped');
    await vi.runOnlyPendingTimersAsync();
    expect(factory).toHaveBeenCalledOnce();
    expect(getMarketDataSnapshot().status).toBe('unavailable');
  });

  it('does not reconnect after an explicit stop', async () => {
    vi.useFakeTimers();
    const factory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: 'canonical-esz6',
      getIdToken: async () => 'token',
      webSocketFactory: factory,
      minReconnectDelayMs: 10,
      random: () => 0,
    });
    await vi.waitFor(() => expect(factory).toHaveBeenCalledOnce());
    supervisor.stop();
    await vi.runOnlyPendingTimersAsync();
    expect(factory).toHaveBeenCalledOnce();
  });
});
