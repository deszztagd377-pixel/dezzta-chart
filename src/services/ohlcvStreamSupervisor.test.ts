import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { getMarketDataSnapshot, resetMarketDataSnapshot } from './marketDataStore';
import { marketDataSeriesStore } from './marketDataSeriesStore';
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
  deferCloseEvent = false;
  throwOnClose = false;
  pendingClose: { code: number; reason: string } | null = null;

  close(code = 1000, reason = '') {
    if (this.throwOnClose) throw new Error('platform close failed');
    if (this.deferCloseEvent) {
      // A browser remains CLOSING until the native close event is delivered.
      this.readyState = 2;
      this.pendingClose = { code, reason };
      return;
    }
    this.readyState = 3;
    this.emitClose(code, reason);
  }
  completeClose() {
    const pending = this.pendingClose;
    if (!pending) throw new Error('No deferred close event is pending.');
    this.pendingClose = null;
    this.readyState = 3;
    this.emitClose(pending.code, pending.reason);
  }
  private emitClose(code: number, reason: string) {
    this.emit('close', Object.assign(new Event('close'), { code, reason }));
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
  provider: 'databento',
  seriesType: 'contract',
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
  streamId: 'stream-a', watermark: 7, cursor: '100',
};

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(async () => ({
    ok: true, status: 200,
    json: async () => ({ ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890', expiresIn: 90, purpose: 'market-data' }),
  }) as unknown as Response));
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
  resetMarketDataSnapshot(null, 'demo', 'test reset');
  marketDataSeriesStore.reset(identity, 'unavailable', 'test reset');
  marketDataSeriesStore.reset({ ...identity, timeframe: '1m' }, 'unavailable', 'test reset');
});

describe('OHLCV stream supervisor', () => {
  it('requests an ID token and publishes the validated snapshot into the shared store', async () => {
    const socket = new FakeSocket();
    const getIdToken = vi.fn().mockResolvedValue('fresh-id-token');
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      webSocketFactory: () => socket as unknown as WebSocket,
      random: () => 0,
    });
    await vi.waitFor(() => expect(getIdToken).toHaveBeenCalledOnce());
    await vi.waitFor(() => expect(socket.listeners.has('open')).toBe(true));
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    expect(JSON.parse(socket.sent[0])).toEqual({ type: 'auth', ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890' });
    socket.message({ type: 'market_data.status', version: 1 });
    expect(JSON.parse(socket.sent[1])).toMatchObject({
      type: 'market_data.subscribe',
      version: 1,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
    });
    socket.message(snapshot);

    expect(supervisor.status).toBe('subscribed');
    expect(getMarketDataSnapshot().source).toBe('backend');
    expect(getMarketDataSnapshot().bars).toHaveLength(1);
    expect(marketDataSeriesStore.getSnapshot(identity).source).toBe('backend');
    expect(marketDataSeriesStore.getSnapshot(identity).bars).toHaveLength(1);
    supervisor.stop();
    expect(supervisor.status).toBe('stopped');
    expect(getMarketDataSnapshot().bars).toHaveLength(0);
    expect(marketDataSeriesStore.getSnapshot(identity).status).toBe('unavailable');
    expect(marketDataSeriesStore.getSnapshot(identity).bars).toHaveLength(0);
  });

  it('supersedes the previous supervisor on timeframe change without allowing stale callbacks to replace the new series', async () => {
    const oldSocket = new FakeSocket();
    oldSocket.deferCloseEvent = true;
    const oldSupervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-id-token',
      webSocketFactory: () => oldSocket as unknown as WebSocket,
      random: () => 0,
    });

    await vi.waitFor(() => expect(oldSocket.listeners.has('open')).toBe(true));
    oldSocket.readyState = 1;
    oldSocket.emit('open', new Event('open'));
    oldSocket.message({ type: 'market_data.status', version: 1 });
    oldSocket.message(snapshot);
    expect(oldSupervisor.status).toBe('subscribed');
    expect(getMarketDataSnapshot().identity?.timeframe).toBe('1s');
    expect(getMarketDataSnapshot().bars).toHaveLength(1);

    const nextSocket = new FakeSocket();
    const nextIdentity = { ...identity, timeframe: '1m' as const };
    const nextSupervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity: nextIdentity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-id-token',
      webSocketFactory: () => nextSocket as unknown as WebSocket,
      random: () => 0,
    });

    expect(oldSupervisor.status).toBe('stopped');
    // The old browser socket is still CLOSING; its native close event arrives later.
    expect(oldSocket.readyState).toBe(2);
    expect(getMarketDataSnapshot().identity?.timeframe).toBe('1m');
    expect(getMarketDataSnapshot().status).toBe('loading');
    expect(getMarketDataSnapshot().bars).toHaveLength(0);

    await vi.waitFor(() => expect(nextSocket.listeners.has('open')).toBe(true));
    nextSocket.readyState = 1;
    nextSocket.emit('open', new Event('open'));
    nextSocket.message({ type: 'market_data.status', version: 1 });
    const nextBar = { ...bar, timeframe: '1m' };
    nextSocket.message({ ...snapshot, bars: [nextBar] });
    expect(getMarketDataSnapshot().identity?.timeframe).toBe('1m');
    expect(getMarketDataSnapshot().bars).toHaveLength(1);
    expect(marketDataSeriesStore.getSnapshot(nextIdentity).bars).toHaveLength(1);

    // Both a queued data message and a delayed native close from the old socket
    // must be harmless after the replacement has published its own snapshot.
    oldSocket.message(snapshot);
    oldSocket.completeClose();
    expect(getMarketDataSnapshot().identity?.timeframe).toBe('1m');
    expect(getMarketDataSnapshot().bars).toEqual([{
      timestamp: 1793577600,
      open: 6000.125,
      high: 6001.25,
      low: 5999.875,
      close: 6000.75,
      volume: 12,
    }]);
    expect(marketDataSeriesStore.getSnapshot(nextIdentity).bars).toHaveLength(1);

    nextSupervisor.stop();
    expect(nextSupervisor.status).toBe('stopped');
  });

  it('resumes from the last accepted cursor after a transport reconnect without clearing the chart', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
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
    expect(getMarketDataSnapshot().bars).toHaveLength(1);

    sockets[0].serverClose(1006, 'network interrupted');
    expect(supervisor.status).toBe('reconnecting');
    expect(getMarketDataSnapshot().bars).toHaveLength(1);

    await vi.advanceTimersByTimeAsync(50);
    await vi.waitFor(() => expect(sockets).toHaveLength(2));
    sockets[1].readyState = 1;
    sockets[1].emit('open', new Event('open'));
    sockets[1].message({ type: 'market_data.status', version: 1 });
    expect(JSON.parse(sockets[1].sent[1])).toMatchObject({
      type: 'market_data.subscribe',
      cursor: '100',
    });

    sockets[1].message({
      type: 'market_data.ohlcv.replay_started',
      version: 1,
      streamId: 'stream-b',
      fromCursor: '100',
      throughCursor: '101',
      count: 1,
    });
    sockets[1].message({
      type: 'market_data.ohlcv.update',
      version: 1,
      streamId: 'stream-b',
      eventId: 'replayed-event',
      cursor: '101',
      sequence: 1,
      emittedAtNs: '1793577602000000000',
      operation: 'upsert',
      isFinal: true,
      series: identity,
      bar: { ...bar, sequence: 8, close: '6001.000', high: '6001.250' },
      replayed: true,
    });
    sockets[1].message({
      type: 'market_data.ohlcv.replay_complete',
      version: 1,
      cursor: '101',
      count: 1,
    });

    expect(supervisor.status).toBe('subscribed');
    expect(getMarketDataSnapshot().bars).toHaveLength(1);
    expect(getMarketDataSnapshot().bars[0].close).toBe(6001);
    supervisor.stop();
  });

  it('drops a stale resume cursor after server-directed resnapshot and adopts only the new snapshot cursor', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
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

    sockets[0].serverClose(1006, 'network interrupted');
    await vi.advanceTimersByTimeAsync(50);
    await vi.waitFor(() => expect(sockets).toHaveLength(2));
    sockets[1].readyState = 1;
    sockets[1].emit('open', new Event('open'));
    sockets[1].message({ type: 'market_data.status', version: 1 });
    expect(JSON.parse(sockets[1].sent[1])).toMatchObject({
      type: 'market_data.subscribe',
      cursor: '100',
    });

    sockets[1].message({
      type: 'market_data.ohlcv.resnapshot_required',
      version: 1,
      reason: 'live_queue_handoff_failed',
      snapshotCursor: '105',
    });
    sockets[1].serverClose(1013, 'Resnapshot required');

    await vi.advanceTimersByTimeAsync(50);
    await vi.waitFor(() => expect(sockets).toHaveLength(3));
    sockets[2].readyState = 1;
    sockets[2].emit('open', new Event('open'));
    sockets[2].message({ type: 'market_data.status', version: 1 });
    const freshSubscribe = JSON.parse(sockets[2].sent[1]);
    expect(freshSubscribe.type).toBe('market_data.subscribe');
    expect(freshSubscribe).not.toHaveProperty('cursor');

    sockets[2].message({ ...snapshot, streamId: 'stream-fresh', cursor: '105' });
    expect(supervisor.status).toBe('subscribed');

    sockets[2].serverClose(1006, 'fresh snapshot connection interrupted');
    await vi.advanceTimersByTimeAsync(50);
    await vi.waitFor(() => expect(sockets).toHaveLength(4));
    sockets[3].readyState = 1;
    sockets[3].emit('open', new Event('open'));
    sockets[3].message({ type: 'market_data.status', version: 1 });
    expect(JSON.parse(sockets[3].sent[1])).toMatchObject({
      type: 'market_data.subscribe',
      cursor: '105',
    });

    supervisor.stop();
  });

  it('resets reconnect backoff after a cursor replay recovers the stream', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const factory = vi.fn(() => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    const getIdToken = vi.fn().mockResolvedValue('fresh-token');
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      webSocketFactory: factory,
      minReconnectDelayMs: 100,
      maxReconnectDelayMs: 400,
      random: () => 0,
    });

    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].readyState = 1;
    sockets[0].emit('open', new Event('open'));
    sockets[0].message({ type: 'market_data.status', version: 1 });
    sockets[0].message({ ...snapshot, watermark: 0, cursor: '100' });

    sockets[0].serverClose(1006, 'first network interruption');
    await vi.advanceTimersByTimeAsync(50);
    await vi.waitFor(() => expect(sockets).toHaveLength(2));

    sockets[1].readyState = 1;
    sockets[1].emit('open', new Event('open'));
    sockets[1].message({ type: 'market_data.status', version: 1 });
    sockets[1].message({
      type: 'market_data.ohlcv.replay_started',
      version: 1,
      streamId: 'stream-replay',
      fromCursor: '100',
      throughCursor: '100',
      count: 0,
    });
    sockets[1].message({
      type: 'market_data.ohlcv.replay_complete',
      version: 1,
      cursor: '100',
      count: 0,
    });
    expect(supervisor.status).toBe('subscribed');

    sockets[1].serverClose(1006, 'second network interruption');
    expect(supervisor.status).toBe('reconnecting');
    await vi.advanceTimersByTimeAsync(49);
    expect(factory).toHaveBeenCalledTimes(2);
    await vi.advanceTimersByTimeAsync(1);
    await vi.waitFor(() => expect(sockets).toHaveLength(3));
    expect(getIdToken).toHaveBeenCalledTimes(3);
    supervisor.stop();
  });

  it('seeds the backend store from the first validated update after an empty snapshot', async () => {
    const socket = new FakeSocket();
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-id-token',
      webSocketFactory: () => socket as unknown as WebSocket,
      random: () => 0,
    });
    await vi.waitFor(() => expect(socket.listeners.has('open')).toBe(true));
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message({
      type: 'market_data.ohlcv.snapshot',
      version: 1,
      state: 'unavailable',
      feedState: 'live',
      timestampUnit: 'nanoseconds',
      priceRepresentation: 'decimal-string',
      count: 0,
      truncated: false,
      bars: [],
      detail: 'No bars yet.',
      streamId: 'stream-a',
      watermark: 0,
    });
    expect(getMarketDataSnapshot().status).toBe('unavailable');
    expect(getMarketDataSnapshot().bars).toHaveLength(0);

    socket.message({
      type: 'market_data.ohlcv.update',
      version: 1,
      streamId: 'stream-a',
      eventId: 'first-event',
      sequence: 1,
      emittedAtNs: '1793577601000000000',
      operation: 'upsert',
      isFinal: true,
      series: identity,
      bar: { ...bar, sequence: 1 },
    });

    expect(getMarketDataSnapshot().source).toBe('backend');
    expect(getMarketDataSnapshot().status).toBe('degraded');
    expect(getMarketDataSnapshot().bars).toHaveLength(1);
    expect(getMarketDataSnapshot().bars[0].close).toBe(6000.75);
    supervisor.stop();
  });

  it('continues reconnecting when supervisor status and error observers throw', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const factory = vi.fn(() => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    const onStatus = vi.fn(() => {
      throw new Error('consumer status observer failed');
    });
    const onError = vi.fn(() => {
      throw new Error('consumer error observer failed');
    });
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
      webSocketFactory: factory,
      onStatus,
      onError,
      minReconnectDelayMs: 100,
      maxReconnectDelayMs: 400,
      random: () => 0,
    });

    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].readyState = 1;
    sockets[0].emit('open', new Event('open'));
    sockets[0].message({ type: 'market_data.status', version: 1 });
    sockets[0].message(snapshot);
    expect(supervisor.status).toBe('subscribed');

    expect(() => sockets[0].emit('error', new Event('error'))).not.toThrow();
    expect(supervisor.status).toBe('reconnecting');
    expect(onError).toHaveBeenCalledOnce();

    await vi.advanceTimersByTimeAsync(49);
    expect(factory).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(1);
    await vi.waitFor(() => expect(sockets).toHaveLength(2));
    expect(factory).toHaveBeenCalledTimes(2);
    expect(supervisor.status).toBe('connecting');
    supervisor.stop();
  });

  it('reconnects when transport failure is followed by a throwing socket.close', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const factory = vi.fn(() => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    const onError = vi.fn();
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
      webSocketFactory: factory,
      onError,
      minReconnectDelayMs: 100,
      maxReconnectDelayMs: 400,
      random: () => 0,
    });

    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].readyState = 1;
    sockets[0].emit('open', new Event('open'));
    sockets[0].message({ type: 'market_data.status', version: 1 });
    sockets[0].message(snapshot);
    sockets[0].throwOnClose = true;

    expect(() => sockets[0].emit('error', new Event('error'))).not.toThrow();
    expect(onError).toHaveBeenCalledOnce();
    expect(supervisor.status).toBe('reconnecting');

    await vi.advanceTimersByTimeAsync(49);
    expect(factory).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(1);
    await vi.waitFor(() => expect(sockets).toHaveLength(2));
    expect(factory).toHaveBeenCalledTimes(2);
    supervisor.stop();
  });

  it('retries after the HTTPS WebSocket-ticket endpoint fails transiently', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const requestWebSocketTicket = vi.fn()
      .mockRejectedValueOnce(new Error('market-data ticket request timed out'))
      .mockResolvedValue('ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890');
    const getIdToken = vi.fn().mockResolvedValue('fresh-token');

    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      requestWebSocketTicket,
      webSocketFactory: () => {
        const socket = new FakeSocket();
        sockets.push(socket);
        return socket as unknown as WebSocket;
      },
      minReconnectDelayMs: 100,
      maxReconnectDelayMs: 400,
      random: () => 0,
    });

    // The initial ticket request fails before a WebSocket is constructed.
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
    expect(supervisor.status).toBe('reconnecting');
    expect(requestWebSocketTicket).toHaveBeenCalledOnce();
    expect(sockets).toHaveLength(0);

    await vi.advanceTimersByTimeAsync(49);
    expect(requestWebSocketTicket).toHaveBeenCalledOnce();
    expect(sockets).toHaveLength(0);

    await vi.advanceTimersByTimeAsync(1);
    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    expect(getIdToken).toHaveBeenCalledTimes(2);
    expect(requestWebSocketTicket).toHaveBeenCalledTimes(2);
    expect(requestWebSocketTicket).toHaveBeenNthCalledWith(
      1, 'https://market.example.test', 'fresh-token',
    );
    expect(requestWebSocketTicket).toHaveBeenNthCalledWith(
      2, 'https://market.example.test', 'fresh-token',
    );
    expect(supervisor.status).toBe('connecting');
    supervisor.stop();
  });

  it('retries after a transient identity-token acquisition failure', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const getIdToken = vi.fn()
      .mockRejectedValueOnce(new Error('temporary token service failure'))
      .mockResolvedValue('fresh-token-after-retry');
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      webSocketFactory: () => {
        const socket = new FakeSocket();
        sockets.push(socket);
        return socket as unknown as WebSocket;
      },
      minReconnectDelayMs: 100,
      maxReconnectDelayMs: 400,
      random: () => 0,
    });

    expect(getIdToken).toHaveBeenCalledOnce();
    // Flush the nested async rejection/finally continuations without advancing fake time.
    await Promise.resolve();
    await Promise.resolve();
    await Promise.resolve();
    expect(supervisor.status).toBe('reconnecting');
    expect(sockets).toHaveLength(0);

    await vi.advanceTimersByTimeAsync(49);
    expect(sockets).toHaveLength(0);
    await vi.advanceTimersByTimeAsync(1);
    expect(sockets).toHaveLength(1);
    expect(getIdToken).toHaveBeenCalledTimes(2);
    supervisor.stop();
  });

  it('retries when Firebase ID-token acquisition never settles', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const getIdToken = vi.fn()
      .mockImplementationOnce(() => new Promise<string>(() => {}))
      .mockResolvedValue('fresh-token-after-timeout');
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      identityTokenTimeoutMs: 25,
      webSocketFactory: () => {
        const socket = new FakeSocket();
        sockets.push(socket);
        return socket as unknown as WebSocket;
      },
      minReconnectDelayMs: 10,
      maxReconnectDelayMs: 10,
      random: () => 0,
    });

    expect(getIdToken).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(30);

    expect(getIdToken).toHaveBeenCalledTimes(2);
    expect(sockets).toHaveLength(1);
    expect(supervisor.status).toBe('connecting');
    supervisor.stop();
  });

  it('bounds Firebase ID-token acquisition during ticket renewal', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const neverSettles = new Promise<string>(() => {});
    const getIdToken = vi.fn()
      .mockResolvedValueOnce('initial-token')
      .mockReturnValueOnce(neverSettles)
      .mockResolvedValue('token-after-renewal-timeout');
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      identityTokenTimeoutMs: 25,
      ticketRenewalIntervalMs: 5_000,
      webSocketFactory: () => {
        const socket = new FakeSocket();
        sockets.push(socket);
        return socket as unknown as WebSocket;
      },
      minReconnectDelayMs: 10,
      maxReconnectDelayMs: 10,
      random: () => 0,
    });

    // Flush the resolved token + ticket HTTP promises without allowing the
    // short timeout used by this test to advance before the socket is created.
    for (let index = 0; index < 8; index += 1) await Promise.resolve();
    expect(sockets).toHaveLength(1);
    sockets[0].readyState = 1;
    sockets[0].emit('open', new Event('open'));
    sockets[0].message({ type: 'market_data.status', version: 1 });
    sockets[0].message(snapshot);
    expect(supervisor.status).toBe('subscribed');

    await vi.advanceTimersByTimeAsync(5_030);
    for (let index = 0; index < 8; index += 1) await Promise.resolve();

    expect(getIdToken).toHaveBeenCalledTimes(3);
    expect(sockets).toHaveLength(2);
    expect(supervisor.status).toBe('connecting');
    supervisor.stop();
  });

  it('uses bounded exponential reconnect and requests a fresh token for the next attempt', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    let tokenCount = 0;
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
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

  it('recovers from a sequence gap only after a fresh snapshot establishes the new watermark', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const getIdToken = vi.fn()
      .mockResolvedValueOnce('token-before-gap')
      .mockResolvedValue('token-after-gap');
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
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
    expect(getMarketDataSnapshot().bars).toHaveLength(1);

    sockets[0].message({
      type: 'market_data.ohlcv.update',
      version: 1,
      streamId: 'stream-a',
      eventId: 'gap-event',
      sequence: 9,
      emittedAtNs: '1793577601000000000',
      operation: 'upsert',
      isFinal: true,
      series: identity,
      bar: { ...bar, sequence: 9 },
    });
    expect(supervisor.status).toBe('reconnecting');

    await vi.advanceTimersByTimeAsync(50);
    await vi.waitFor(() => expect(sockets).toHaveLength(2));
    sockets[1].readyState = 1;
    sockets[1].emit('open', new Event('open'));
    sockets[1].message({ type: 'market_data.status', version: 1 });
    sockets[1].message({
      ...snapshot,
      streamId: 'stream-b',
      watermark: 20,
      bars: [{ ...bar, sequence: 20, close: '6001.000' }],
    });

    sockets[1].message({
      type: 'market_data.ohlcv.update',
      version: 1,
      streamId: 'stream-b',
      eventId: 'recovered-event',
      sequence: 21,
      emittedAtNs: '1793577602000000000',
      operation: 'upsert',
      isFinal: true,
      series: identity,
      bar: { ...bar, sequence: 21, high: '6002.000', close: '6002.000' },
    });

    expect(supervisor.status).toBe('subscribed');
    expect(getIdToken).toHaveBeenCalledTimes(2);
    expect(getMarketDataSnapshot().source).toBe('backend');
    expect(getMarketDataSnapshot().bars).toHaveLength(1);
    expect(getMarketDataSnapshot().bars[0].close).toBe(6002);
    supervisor.stop();
  });

  it.each(['', '   '])(
    'stops without retrying when the identity provider returns an empty token (%j)',
    async (emptyToken) => {
      vi.useFakeTimers();
      const factory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
      const onError = vi.fn();
      const supervisor = startOhlcvStreamSupervisor({
        baseUrl: 'https://market.example.test',
        identity,
        canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
        getIdToken: async () => emptyToken,
        webSocketFactory: factory,
        onError,
        minReconnectDelayMs: 10,
        random: () => 0,
      });

      await vi.waitFor(() => expect(supervisor.status).toBe('stopped'));
      await vi.advanceTimersByTimeAsync(1_000);

      expect(factory).not.toHaveBeenCalled();
      expect(onError).toHaveBeenCalledOnce();
      expect(getMarketDataSnapshot().status).toBe('unavailable');
      supervisor.stop();
    },
  );


  it('stops without retrying when the HTTPS ticket endpoint rejects authentication', async () => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', vi.fn(async () => ({
      ok: false,
      status: 401,
    }) as unknown as Response));
    const factory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
    const onError = vi.fn();
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
      webSocketFactory: factory,
      onError,
      minReconnectDelayMs: 10,
      random: () => 0,
    });
    await vi.waitFor(() => expect(supervisor.status).toBe('stopped'));
    await vi.advanceTimersByTimeAsync(1_000);
    expect(factory).not.toHaveBeenCalled();
    expect(onError).toHaveBeenCalledOnce();
    supervisor.stop();
  });

  it('does not retry after entitlement denial and reports the correct cause', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const factory = vi.fn(() => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    const onError = vi.fn();
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
      webSocketFactory: factory,
      onError,
      minReconnectDelayMs: 10,
      random: () => 0,
    });
    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].serverClose(4403, 'Instrument access denied');
    expect(supervisor.status).toBe('stopped');
    await vi.runOnlyPendingTimersAsync();
    expect(factory).toHaveBeenCalledOnce();
    expect(getMarketDataSnapshot().status).toBe('unavailable');
    expect(getMarketDataSnapshot().detail).toMatch(/not entitled|access was revoked/i);
    expect(onError).toHaveBeenCalledWith(expect.objectContaining({ message: expect.stringMatching(/entitlement denied/i) }));
  });

  it('does not misreport an Origin rejection as an entitlement failure', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const factory = vi.fn(() => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    const onError = vi.fn();
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
      webSocketFactory: factory,
      onError,
      minReconnectDelayMs: 10,
      random: () => 0,
    });
    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].serverClose(4403, 'Origin not allowed');
    expect(supervisor.status).toBe('stopped');
    expect(getMarketDataSnapshot().detail).toMatch(/Origin is not allowlisted/i);
    expect(onError).toHaveBeenCalledWith(expect.objectContaining({ message: expect.stringMatching(/Origin rejected/i) }));
    await vi.runOnlyPendingTimersAsync();
    expect(factory).toHaveBeenCalledOnce();
  });

  it('does not retry after a server protocol-policy close (1008)', async () => {
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
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
      webSocketFactory: factory,
      minReconnectDelayMs: 10,
      random: () => 0,
    });

    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].serverClose(1008, 'WebSocket ping rate limit exceeded');

    expect(supervisor.status).toBe('stopped');
    expect(getMarketDataSnapshot().status).toBe('unavailable');
    await vi.runOnlyPendingTimersAsync();
    expect(factory).toHaveBeenCalledOnce();
    supervisor.stop();
  });

  it('schedules only one reconnect when a transport error and close event race', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const getIdToken = vi.fn().mockResolvedValue('fresh-token');
    const factory = vi.fn(() => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      webSocketFactory: factory,
      minReconnectDelayMs: 100,
      maxReconnectDelayMs: 400,
      random: () => 0,
    });

    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].readyState = 1;
    sockets[0].emit('error', new Event('error'));
    // The transport's error handler closes the socket, which emits close.
    // A second close notification must not create another retry timer.
    sockets[0].emit('close', Object.assign(new Event('close'), { code: 1006, reason: 'duplicate close' }));

    expect(supervisor.status).toBe('reconnecting');
    await vi.advanceTimersByTimeAsync(49);
    expect(factory).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(1);
    await vi.waitFor(() => expect(sockets).toHaveLength(2));
    expect(factory).toHaveBeenCalledTimes(2);
    expect(getIdToken).toHaveBeenCalledTimes(2);
    supervisor.stop();
  });

  it('waits for the transport close event before opening a replacement connection', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const factory = vi.fn(() => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    const getIdToken = vi.fn().mockResolvedValue('fresh-token');
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      webSocketFactory: factory,
      minReconnectDelayMs: 100,
      maxReconnectDelayMs: 400,
      random: () => 0,
    });

    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].deferCloseEvent = true;
    sockets[0].readyState = 1;
    sockets[0].emit('error', new Event('error'));

    expect(supervisor.status).toBe('reconnecting');
    // An error is advisory; no second socket may open before the old socket closes.
    await vi.advanceTimersByTimeAsync(1_000);
    expect(factory).toHaveBeenCalledOnce();
    expect(getIdToken).toHaveBeenCalledOnce();

    sockets[0].completeClose();
    await vi.advanceTimersByTimeAsync(49);
    expect(factory).toHaveBeenCalledOnce();
    await vi.advanceTimersByTimeAsync(1);
    await vi.waitFor(() => expect(sockets).toHaveLength(2));
    expect(getIdToken).toHaveBeenCalledTimes(2);
    supervisor.stop();
  });

  it('cancels a scheduled reconnect when stopped before the retry deadline', async () => {
    vi.useFakeTimers();
    const sockets: FakeSocket[] = [];
    const factory = vi.fn(() => {
      const socket = new FakeSocket();
      sockets.push(socket);
      return socket as unknown as WebSocket;
    });
    const getIdToken = vi.fn().mockResolvedValue('fresh-token');
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      webSocketFactory: factory,
      minReconnectDelayMs: 100,
      maxReconnectDelayMs: 400,
      random: () => 0,
    });

    await vi.waitFor(() => expect(sockets).toHaveLength(1));
    sockets[0].readyState = 1;
    sockets[0].emit('error', new Event('error'));
    expect(supervisor.status).toBe('reconnecting');
    supervisor.stop();
    await vi.advanceTimersByTimeAsync(1_000);

    expect(factory).toHaveBeenCalledOnce();
    expect(getIdToken).toHaveBeenCalledOnce();
    expect(supervisor.status).toBe('stopped');
  });

  it('cancels a superseded supervisor while its Firebase token request is pending', async () => {
    vi.useFakeTimers();
    let resolveOldToken!: (token: string) => void;
    const oldTokenPromise = new Promise<string>((resolve) => {
      resolveOldToken = resolve;
    });
    const oldFactory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
    const oldSupervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: () => oldTokenPromise,
      webSocketFactory: oldFactory,
      random: () => 0,
    });

    const replacementSocket = new FakeSocket();
    const replacementIdentity = { ...identity, timeframe: '5s' as const };
    const replacementSupervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity: replacementIdentity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'replacement-token',
      webSocketFactory: () => replacementSocket as unknown as WebSocket,
      random: () => 0,
    });

    expect(oldSupervisor.status).toBe('stopped');
    resolveOldToken('late-old-token');
    await Promise.resolve();
    await Promise.resolve();
    expect(oldFactory).not.toHaveBeenCalled();
    expect(replacementSupervisor.status).toBe('connecting');
    expect(getMarketDataSnapshot().identity?.timeframe).toBe('5s');

    await vi.waitFor(() => expect(replacementSocket.listeners.has('open')).toBe(true));
    replacementSupervisor.stop();
  });

  it('does not open a socket when stop occurs while ID-token acquisition is pending', async () => {
    vi.useFakeTimers();
    let resolveToken!: (token: string) => void;
    const tokenPromise = new Promise<string>((resolve) => {
      resolveToken = resolve;
    });
    const getIdToken = vi.fn(() => tokenPromise);
    const factory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      webSocketFactory: factory,
      minReconnectDelayMs: 10,
      random: () => 0,
    });

    expect(getIdToken).toHaveBeenCalledOnce();
    supervisor.stop();
    resolveToken('late-token');
    await Promise.resolve();
    await Promise.resolve();
    await vi.advanceTimersByTimeAsync(1_000);

    expect(factory).not.toHaveBeenCalled();
    expect(getIdToken).toHaveBeenCalledOnce();
    expect(supervisor.status).toBe('stopped');
  });

  it('does not schedule a retry when a pending token request rejects after stop', async () => {
    vi.useFakeTimers();
    let rejectToken!: (error: Error) => void;
    const tokenPromise = new Promise<string>((_resolve, reject) => {
      rejectToken = reject;
    });
    const getIdToken = vi.fn(() => tokenPromise);
    const factory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken,
      webSocketFactory: factory,
      minReconnectDelayMs: 10,
      random: () => 0,
    });

    supervisor.stop();
    rejectToken(new Error('token request completed after stop'));
    await Promise.resolve();
    await Promise.resolve();
    await vi.advanceTimersByTimeAsync(1_000);

    expect(factory).not.toHaveBeenCalled();
    expect(getIdToken).toHaveBeenCalledOnce();
    expect(supervisor.status).toBe('stopped');
  });

  it('does not open a socket when stop occurs while ticket issuance is pending', async () => {
    vi.useFakeTimers();
    let resolveTicket!: (ticket: string) => void;
    const ticketPromise = new Promise<string>((resolve) => {
      resolveTicket = resolve;
    });
    const requestWebSocketTicket = vi.fn(() => ticketPromise);
    const factory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
      requestWebSocketTicket,
      webSocketFactory: factory,
      minReconnectDelayMs: 10,
      random: () => 0,
    });

    for (let index = 0; index < 8; index += 1) await Promise.resolve();
    expect(requestWebSocketTicket).toHaveBeenCalledOnce();
    expect(factory).not.toHaveBeenCalled();

    supervisor.stop();
    resolveTicket('late-ticket-abcdefghijklmnopqrstuvwxyz1234567890');
    for (let index = 0; index < 8; index += 1) await Promise.resolve();
    await vi.advanceTimersByTimeAsync(1_000);

    expect(factory).not.toHaveBeenCalled();
    expect(requestWebSocketTicket).toHaveBeenCalledOnce();
    expect(supervisor.status).toBe('stopped');
  });

  it('does not republish late snapshot or update messages after supervisor stop', async () => {
    const socket = new FakeSocket();
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      getIdToken: async () => 'fresh-token',
      webSocketFactory: () => socket as unknown as WebSocket,
      random: () => 0,
    });

    await vi.waitFor(() => expect(socket.listeners.has('open')).toBe(true));
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);
    expect(getMarketDataSnapshot().source).toBe('backend');
    expect(getMarketDataSnapshot().bars).toHaveLength(1);

    supervisor.stop();
    expect(getMarketDataSnapshot().status).toBe('unavailable');
    expect(getMarketDataSnapshot().detail).toBe('OHLCV stream stopped.');

    socket.message({ ...snapshot, streamId: 'late-stream', watermark: 99 });
    socket.message({
      type: 'market_data.ohlcv.update',
      version: 1,
      streamId: 'stream-a',
      eventId: 'late-update',
      sequence: 8,
      emittedAtNs: '1793577601000000000',
      operation: 'upsert',
      isFinal: true,
      series: identity,
      bar: { ...bar, sequence: 8, close: '7000.000' },
    });

    expect(supervisor.status).toBe('stopped');
    expect(getMarketDataSnapshot().status).toBe('unavailable');
    expect(getMarketDataSnapshot().detail).toBe('OHLCV stream stopped.');
    expect(getMarketDataSnapshot().bars).toHaveLength(0);
  });

  it('does not reconnect after an explicit stop', async () => {
    vi.useFakeTimers();
    const factory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
    const supervisor = startOhlcvStreamSupervisor({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
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
