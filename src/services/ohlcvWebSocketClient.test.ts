import { afterEach, describe, expect, it, vi } from 'vitest';
import { connectOhlcvStream } from './ohlcvWebSocketClient';

class FakeSocket {
  readyState = 0;
  sent: string[] = [];
  closed: Array<{ code: number; reason: string }> = [];
  private listeners = new Map<string, Array<(event: Event) => void>>();

  addEventListener(type: string, listener: EventListenerOrEventListenerObject) {
    const callback = typeof listener === 'function'
      ? listener as (event: Event) => void
      : (event: Event) => listener.handleEvent(event);
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), callback]);
  }

  send(value: string) { this.sent.push(value); }
  close(code = 1000, reason = '') {
    this.readyState = 3;
    this.closed.push({ code, reason });
    this.emit('close', new Event('close'));
  }
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
const snapshot = {
  type: 'market_data.ohlcv.snapshot',
  version: 1,
  state: 'ready',
  feedState: 'live',
  timestampUnit: 'nanoseconds',
  priceRepresentation: 'decimal-string',
  count: 1,
  truncated: false,
  bars: [bar],
  detail: null,
  streamId: 'stream-a',
  watermark: 7,
};
const update = {
  type: 'market_data.ohlcv.update',
  version: 1,
  streamId: 'stream-a',
  eventId: 'event-8',
  sequence: 8,
  emittedAtNs: '1793577601000000000',
  operation: 'upsert',
  isFinal: true,
  series: identity,
  bar: { ...bar, sequence: 8, close: '6001.000' },
};

function setup() {
  const socket = new FakeSocket();
  const onSnapshot = vi.fn();
  const onUpdate = vi.fn();
  const onError = vi.fn();
  const connection = connectOhlcvStream({
    baseUrl: 'https://market.example.test/api/',
    identity,
    canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
    token: 'verified-token',
    webSocketFactory: () => socket as unknown as WebSocket,
    onSnapshot,
    onUpdate,
    onError,
  });
  return { socket, onSnapshot, onUpdate, onError, connection };
}

afterEach(() => {
  vi.useRealTimers();
});

describe('connectOhlcvStream', () => {
  it('authenticates, requests an exact series, then applies snapshot and next update', () => {
    const { socket, onSnapshot, onUpdate, connection } = setup();
    expect(connection.state).toBe('connecting');
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    expect(JSON.parse(socket.sent[0])).toEqual({ type: 'auth', token: 'verified-token' });

    socket.message({
      type: 'market_data.status',
      version: 1,
      dataset: 'GLBX.MDP3',
      schema: 'ohlcv',
      quality: { state: 'live' },
    });
    expect(connection.state).toBe('authenticated');
    expect(JSON.parse(socket.sent[1])).toMatchObject({
      type: 'market_data.subscribe',
      version: 1,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      series: { ...identity, bucketPolicy: 'UTC_FIXED_V1' },
    });

    socket.message(snapshot);
    expect(connection.state).toBe('subscribed');
    expect(onSnapshot).toHaveBeenCalledOnce();
    expect(onSnapshot.mock.calls[0][1]).toHaveLength(1);

    socket.message(update);
    expect(onUpdate).toHaveBeenCalledOnce();
    expect(onUpdate.mock.calls[0][0].sequence).toBe(8);
    expect(onUpdate.mock.calls[0][1].close).toBe(6001);
  });

  it('does not let the handshake timeout close a stream after its snapshot is accepted', () => {
    vi.useFakeTimers();
    const { socket, onError, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);

    expect(connection.state).toBe('subscribed');
    vi.advanceTimersByTime(10_000);

    expect(connection.state).toBe('subscribed');
    expect(onError).not.toHaveBeenCalled();
    expect(socket.closed).toHaveLength(0);
    connection.close();
  });

  it('rejects a sequence gap and closes instead of silently skipping data', () => {
    const { socket, onError, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);
    socket.message({ ...update, sequence: 10 });

    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0].message).toMatch(/sequence gap/i);
    expect(connection.state).toBe('closed');
    expect(socket.closed[0].code).toBe(1011);
  });

  it('rejects invalid identity configuration before opening a socket', () => {
    const factory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
    expect(() => connectOhlcvStream({
      baseUrl: 'file:///tmp',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      token: 'token',
      webSocketFactory: factory,
      onSnapshot: vi.fn(),
      onUpdate: vi.fn(),
    })).toThrow(/HTTP/);
    expect(factory).not.toHaveBeenCalled();
  });

  it('closes cleanly when the caller changes contract or timeframe', () => {
    const { socket, connection } = setup();
    socket.readyState = 1;
    connection.close();
    expect(connection.state).toBe('closed');
    expect(socket.closed[0]).toEqual({
      code: 1000,
      reason: 'Client closed OHLCV stream',
    });
  });
});
