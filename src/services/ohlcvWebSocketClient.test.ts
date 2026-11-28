import { afterEach, describe, expect, it, vi } from 'vitest';
import { connectOhlcvStream, getStableConsumerInstanceId } from './ohlcvWebSocketClient';

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
  provider: 'databento',
  seriesType: 'contract',
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
const ackUpdate = {
  ...update,
  cursor: '8',
  generationId: 'stream-a',
  digest: '28d8b04abd0a25acd1c4dcd177d64d14ef959675a456dc277c30e6376afa535f',
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
    ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
    webSocketFactory: () => socket as unknown as WebSocket,
    onSnapshot,
    onUpdate,
    onError,
  });
  return { socket, onSnapshot, onUpdate, onError, connection };
}

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe('stable WebSocket consumer instance identity', () => {
  it('persists one non-secret UUID across connection instances', () => {
    const values = new Map<string, string>();
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => values.get(key) ?? null,
      setItem: (key: string, value: string) => values.set(key, value),
    });
    const first = getStableConsumerInstanceId();
    const second = getStableConsumerInstanceId();
    expect(first).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    expect(second).toBe(first);
  });
});

describe('connectOhlcvStream', () => {
  it('rejects plaintext remote WebSocket transport in production before opening a socket', () => {
    vi.stubEnv('PROD', true);
    const webSocketFactory = vi.fn(() => new FakeSocket() as unknown as WebSocket);
    expect(() => connectOhlcvStream({
      baseUrl: 'http://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      webSocketFactory,
      onSnapshot: vi.fn(),
      onUpdate: vi.fn(),
    })).toThrow(/HTTPS\/WSS/i);
    expect(webSocketFactory).not.toHaveBeenCalled();
  });


  it('authenticates, requests an exact series, then applies snapshot and next update', () => {
    const { socket, onSnapshot, onUpdate, connection } = setup();
    expect(connection.state).toBe('connecting');
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    expect(JSON.parse(socket.sent[0])).toEqual({ type: 'auth', ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890' });

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
      clientInstanceId: expect.stringMatching(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i),
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

  it('coalesces durable ACKs and confirms the highest contiguous applied event', () => {
    vi.useFakeTimers();
    const { socket, onError, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1, consumerAckProtocolVersion: 1 });
    socket.message(snapshot);
    socket.message(ackUpdate);
    socket.message({
      ...ackUpdate,
      eventId: 'event-9',
      cursor: '9',
      sequence: 9,
      digest: '2517afa58108b20bbcf9f4e448fbbd5b03ad31b99dc9b0163e617a8f0ee08535',
      emittedAtNs: '1793577602000000000',
      bar: {
        ...bar,
        tsStartNs: '1793577601000000000',
        tsEventNs: '1793577601999000000',
        tsReceivedNs: '1793577602000000000',
        sequence: 9,
        high: '6002.000',
        close: '6002.000',
      },
    });

    expect(onError).not.toHaveBeenCalled();
    vi.advanceTimersByTime(9_999);
    expect(socket.sent.map((value) => JSON.parse(value)).filter((value) => value.type === 'market_data.ack')).toHaveLength(0);
    vi.advanceTimersByTime(1);
    const acknowledgements = socket.sent.map((value) => JSON.parse(value))
      .filter((value) => value.type === 'market_data.ack');
    expect(onError).not.toHaveBeenCalled();
    expect(acknowledgements).toEqual([{
      type: 'market_data.ack',
      version: 1,
      sequence: 9,
      eventDigest: '2517afa58108b20bbcf9f4e448fbbd5b03ad31b99dc9b0163e617a8f0ee08535',
    }]);

    socket.message({
      type: 'market_data.acknowledged',
      version: 1,
      accepted: true,
      duplicate: false,
      committedCursor: '9',
      receiptVersion: 1,
    });
    expect(connection.state).toBe('subscribed');
    expect(onError).not.toHaveBeenCalled();
    connection.close();
  });

  it('does not send consumer ACKs unless the server explicitly advertises the capability', () => {
    vi.useFakeTimers();
    const { socket, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);
    socket.message(ackUpdate);
    vi.advanceTimersByTime(10_000);
    expect(socket.sent.filter((value) => value.startsWith('{')).map((value) => JSON.parse(value))
      .some((value) => value.type === 'market_data.ack')).toBe(false);
    connection.close();
  });

  it('fails closed when the server rejects a durable consumer ACK', () => {
    vi.useFakeTimers();
    const { socket, onError, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1, consumerAckProtocolVersion: 1 });
    socket.message(snapshot);
    socket.message(ackUpdate);
    vi.advanceTimersByTime(10_000);
    socket.message({
      type: 'market_data.ack_rejected',
      version: 1,
      reason: 'consumer_fenced',
    });
    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0].message).toMatch(/consumer ACK: consumer_fenced/i);
    expect(connection.state).toBe('closed');
    expect(socket.closed[0].code).toBe(1011);
  });

  it('resumes from a durable cursor and applies replay before switching to live updates', () => {
    const socket = new FakeSocket();
    const onSnapshot = vi.fn();
    const onUpdate = vi.fn();
    const onCursor = vi.fn();
    const onError = vi.fn();
    const connection = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      resumeCursor: '9007199254740993123',
      onCursor,
      webSocketFactory: () => socket as unknown as WebSocket,
      onSnapshot,
      onUpdate,
      onError,
    });
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    expect(JSON.parse(socket.sent[1])).toMatchObject({
      type: 'market_data.subscribe',
      cursor: '9007199254740993123',
    });

    socket.message({
      type: 'market_data.ohlcv.replay_started',
      version: 1,
      streamId: 'stream-replay',
      fromCursor: '9007199254740993123',
      throughCursor: '9007199254740993124',
      count: 1,
    });
    socket.message({
      ...update,
      streamId: 'stream-replay',
      cursor: '9007199254740993124',
      sequence: 1,
      replayed: true,
    });
    expect(connection.state).toBe('authenticated');
    expect(onUpdate).toHaveBeenCalledOnce();
    expect(onCursor).toHaveBeenLastCalledWith('9007199254740993124');

    socket.message({
      type: 'market_data.ohlcv.replay_complete',
      version: 1,
      cursor: '9007199254740993124',
      count: 1,
    });
    expect(connection.state).toBe('subscribed');
    expect(onCursor).toHaveBeenLastCalledWith('9007199254740993124');

    socket.message({
      ...update,
      streamId: 'stream-replay',
      cursor: '9007199254740993125',
      sequence: 2,
    });
    expect(onUpdate).toHaveBeenCalledTimes(2);
    expect(onError).not.toHaveBeenCalled();
    connection.close();
  });


  it('resumes synthetic replay from explicit stream sequence bounds independently of its cursor', () => {
    const socket = new FakeSocket();
    const onUpdate = vi.fn();
    const onCursor = vi.fn();
    const onError = vi.fn();
    const connection = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      resumeCursor: '50',
      onCursor,
      webSocketFactory: () => socket as unknown as WebSocket,
      onSnapshot: vi.fn(),
      onUpdate,
      onError,
    });
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message({
      type: 'market_data.ohlcv.replay_started',
      version: 1,
      streamId: 'synthetic:series',
      fromCursor: '50',
      throughCursor: '51',
      fromSequence: 50,
      throughSequence: 51,
      count: 1,
    });
    socket.message({
      ...update,
      streamId: 'synthetic:series',
      cursor: '51',
      sequence: 51,
    });
    socket.message({
      type: 'market_data.ohlcv.replay_complete',
      version: 1,
      cursor: '51',
      throughSequence: 51,
      count: 1,
    });
    expect(connection.state).toBe('subscribed');
    expect(onUpdate).toHaveBeenCalledOnce();
    expect(onCursor).toHaveBeenLastCalledWith('51');
    expect(onError).not.toHaveBeenCalled();
    connection.close();
  });

  it('abandons an incomplete replay and accepts the server-directed replacement snapshot', () => {
    const socket = new FakeSocket();
    const onSnapshot = vi.fn();
    const onCursor = vi.fn();
    const onResnapshotRequired = vi.fn();
    const onError = vi.fn();
    const connection = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      resumeCursor: '6',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      webSocketFactory: () => socket as unknown as WebSocket,
      onSnapshot,
      onUpdate: vi.fn(),
      onCursor,
      onResnapshotRequired,
      onError,
    });

    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message({
      type: 'market_data.ohlcv.replay_started',
      version: 1,
      streamId: 'stream-a',
      fromCursor: '6',
      throughCursor: '7',
      count: 1,
    });
    socket.message({
      type: 'market_data.ohlcv.resnapshot_required',
      version: 1,
      reason: 'cursor_expired',
      snapshotCursor: '7',
    });

    expect(connection.state).toBe('authenticated');
    expect(onResnapshotRequired).toHaveBeenCalledOnce();
    expect(onResnapshotRequired).toHaveBeenCalledWith('7');
    socket.message({ ...snapshot, cursor: '7' });

    expect(connection.state).toBe('subscribed');
    expect(onSnapshot).toHaveBeenCalledOnce();
    expect(onCursor).toHaveBeenLastCalledWith('7');
    expect(onError).not.toHaveBeenCalled();
    expect(socket.closed).toHaveLength(0);
    connection.close();
  });

  it('rejects a replacement snapshot whose durable cursor differs from the resnapshot watermark', () => {
    const { socket, onError, onSnapshot, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message({
      type: 'market_data.ohlcv.resnapshot_required',
      version: 1,
      reason: 'cursor_expired',
      snapshotCursor: '7',
    });

    socket.message({ ...snapshot, cursor: '8' });

    expect(connection.state).toBe('closed');
    expect(onSnapshot).not.toHaveBeenCalled();
    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0].message).toMatch(/replacement snapshot cursor/i);
  });

  it('rejects a replacement snapshot that omits its required durable cursor', () => {
    const { socket, onError, onSnapshot, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message({
      type: 'market_data.ohlcv.resnapshot_required',
      version: 1,
      reason: 'cursor_expired',
      snapshotCursor: '7',
    });

    const { cursor: _ignored, ...snapshotWithoutCursor } = snapshot;
    socket.message(snapshotWithoutCursor);

    expect(connection.state).toBe('closed');
    expect(onSnapshot).not.toHaveBeenCalled();
    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0].message).toMatch(/replacement snapshot cursor/i);
  });

  it('rejects malformed server-directed resnapshot instructions', () => {
    const { socket, onError, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message({
      type: 'market_data.ohlcv.resnapshot_required',
      version: 1,
      reason: 'cursor_expired',
      snapshotCursor: 'not-a-cursor',
    });

    expect(connection.state).toBe('closed');
    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0].message).toMatch(/resnapshot instruction is invalid/i);
  });

  it('renews its single-use ticket and waits for server acknowledgement', async () => {
    vi.useFakeTimers();
    const socket = new FakeSocket();
    const getRenewalTicket = vi.fn().mockResolvedValue('renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890');
    const connection = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket,
      heartbeatIntervalMs: 60_000,
      heartbeatTimeoutMs: 10_000,
      webSocketFactory: () => socket as unknown as WebSocket,
      onSnapshot: vi.fn(),
      onUpdate: vi.fn(),
    });
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);
    await vi.advanceTimersByTimeAsync(45_000);
    expect(getRenewalTicket).toHaveBeenCalledOnce();
    expect(JSON.parse(socket.sent[socket.sent.length - 1])).toEqual({ type: 'auth.renew', ticket: 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890' });
    socket.message({ type: 'market_data.auth.renewed', version: 1 });
    expect(connection.state).toBe('subscribed');
    connection.close();
  });

  it('ignores a late ticket-renewal rejection after intentional connection close', async () => {
    vi.useFakeTimers();
    const socket = new FakeSocket();
    let rejectRenewal!: (error: Error) => void;
    const renewalPromise = new Promise<string>((_resolve, reject) => {
      rejectRenewal = reject;
    });
    const getRenewalTicket = vi.fn(() => renewalPromise);
    const onError = vi.fn();
    const connection = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket,
      ticketRenewalIntervalMs: 5_000,
      heartbeatIntervalMs: 60_000,
      heartbeatTimeoutMs: 10_000,
      webSocketFactory: () => socket as unknown as WebSocket,
      onSnapshot: vi.fn(),
      onUpdate: vi.fn(),
      onError,
    });

    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);
    await vi.advanceTimersByTimeAsync(5_000);
    expect(getRenewalTicket).toHaveBeenCalledOnce();

    connection.close();
    rejectRenewal(new Error('identity request cancelled during intentional shutdown'));
    await Promise.resolve();
    await Promise.resolve();

    expect(connection.state).toBe('closed');
    expect(socket.closed).toHaveLength(1);
    expect(socket.closed[0].code).toBe(1000);
    expect(onError).not.toHaveBeenCalled();
  });

  it('sends a text ping heartbeat after subscription and accepts the server pong', () => {
    vi.useFakeTimers();
    const { socket, onError, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);

    expect(connection.state).toBe('subscribed');
    vi.advanceTimersByTime(20_000);
    expect(socket.sent[socket.sent.length - 1]).toBe('ping');

    socket.message({ type: 'market_data.pong', version: 1 });
    vi.advanceTimersByTime(10_000);
    expect(onError).not.toHaveBeenCalled();
    expect(connection.state).toBe('subscribed');
    connection.close();

    const sentBeforeClose = socket.sent.length;
    vi.advanceTimersByTime(60_000);
    expect(socket.sent).toHaveLength(sentBeforeClose);
  });

  it('always closes the transport when the error observer throws', () => {
    const { socket, onError, connection } = setup();
    onError.mockImplementation(() => {
      throw new Error('consumer error observer failed');
    });
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);

    expect(() => socket.message({ type: 'unexpected.message', version: 1 })).not.toThrow();

    expect(onError).toHaveBeenCalledOnce();
    expect(connection.state).toBe('closed');
    expect(socket.closed).toHaveLength(1);
    expect(socket.closed[0].code).toBe(1011);
  });

  it('notifies close exactly once when failure cleanup cannot call socket.close', () => {
    const { socket, connection } = setup();
    const onClose = vi.fn();
    const second = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      webSocketFactory: () => socket as unknown as WebSocket,
      onSnapshot: vi.fn(),
      onUpdate: vi.fn(),
      onClose,
    });
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);
    socket.close = () => {
      throw new Error('platform close failed');
    };

    expect(() => socket.message({ type: 'unexpected.message', version: 1 })).not.toThrow();
    expect(second.state).toBe('closed');
    expect(onClose).toHaveBeenCalledOnce();
    expect(onClose).toHaveBeenCalledWith(1011, 'OHLCV stream failure');

    socket.emit('close', Object.assign(new Event('close'), { code: 1000, reason: 'late close event' }));
    expect(onClose).toHaveBeenCalledOnce();
    connection.close();

    const alreadyClosedSocket = new FakeSocket();
    const alreadyClosedObserver = vi.fn();
    const alreadyClosedConnection = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      webSocketFactory: () => alreadyClosedSocket as unknown as WebSocket,
      onSnapshot: vi.fn(),
      onUpdate: vi.fn(),
      onClose: alreadyClosedObserver,
    });
    alreadyClosedSocket.readyState = 3;
    expect(() => alreadyClosedSocket.message({ type: 'unexpected.message', version: 1 })).not.toThrow();
    expect(alreadyClosedConnection.state).toBe('closed');
    expect(alreadyClosedObserver).toHaveBeenCalledOnce();
    expect(alreadyClosedObserver).toHaveBeenCalledWith(
      1011,
      'OHLCV stream ended before close event',
    );
    alreadyClosedSocket.emit('close', Object.assign(new Event('close'), { code: 1000, reason: 'late close event' }));
    expect(alreadyClosedObserver).toHaveBeenCalledOnce();
  });

  it('isolates a throwing status observer and continues the authenticated handshake', () => {
    const socket = new FakeSocket();
    const onStatus = vi.fn(() => {
      throw new Error('consumer status observer failed');
    });
    const onError = vi.fn();
    const connection = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      webSocketFactory: () => socket as unknown as WebSocket,
      onSnapshot: vi.fn(),
      onUpdate: vi.fn(),
      onStatus,
      onError,
    });

    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    expect(() => socket.message({ type: 'market_data.status', version: 1 })).not.toThrow();
    expect(connection.state).toBe('authenticated');
    expect(JSON.parse(socket.sent[1]).type).toBe('market_data.subscribe');
    expect(onStatus).toHaveBeenCalledWith('authenticated');
    expect(onError).not.toHaveBeenCalled();
    connection.close();
  });

  it('converts an authentication send exception into a terminal transport failure', () => {
    const { socket, onError, connection } = setup();
    socket.send = () => {
      throw new Error('platform send failed');
    };

    expect(() => {
      socket.readyState = 1;
      socket.emit('open', new Event('open'));
    }).not.toThrow();

    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0].message).toMatch(/authentication send failed/i);
    expect(connection.state).toBe('closed');
    expect(socket.closed[0].code).toBe(1011);
  });

  it('reaches closed state when close observers or the platform close call throw', () => {
    const { socket, connection } = setup();
    const onClose = vi.fn(() => {
      throw new Error('consumer close observer failed');
    });
    const secondSocket = new FakeSocket();
    const second = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      webSocketFactory: () => secondSocket as unknown as WebSocket,
      onSnapshot: vi.fn(),
      onUpdate: vi.fn(),
      onClose,
    });
    secondSocket.readyState = 1;
    expect(() => second.close()).not.toThrow();
    expect(second.state).toBe('closed');
    expect(onClose).toHaveBeenCalledOnce();

    socket.close = () => {
      throw new Error('platform close failed');
    };
    expect(() => connection.close()).not.toThrow();
    expect(connection.state).toBe('closed');

    const failedCloseSocket = new FakeSocket();
    const failedCloseObserver = vi.fn();
    const failedCloseConnection = connectOhlcvStream({
      baseUrl: 'https://market.example.test',
      identity,
      canonicalInstrumentId: '11111111-1111-4111-8111-111111111111',
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      webSocketFactory: () => failedCloseSocket as unknown as WebSocket,
      onSnapshot: vi.fn(),
      onUpdate: vi.fn(),
      onClose: failedCloseObserver,
    });
    failedCloseSocket.readyState = 1;
    failedCloseSocket.close = () => {
      throw new Error('platform close failed');
    };

    expect(() => failedCloseConnection.close()).not.toThrow();
    expect(failedCloseConnection.state).toBe('closed');
    expect(failedCloseObserver).toHaveBeenCalledOnce();
    expect(failedCloseObserver).toHaveBeenCalledWith(1006, 'Client close request failed');
  });

  it('rejects an unsolicited heartbeat pong when no ping is outstanding', () => {
    const { socket, onError, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);

    socket.message({ type: 'market_data.pong', version: 1 });

    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0].message).toMatch(/unexpected or invalid.*pong/i);
    expect(connection.state).toBe('closed');
    expect(socket.closed[0].code).toBe(1011);
  });

  it('rejects a heartbeat pong with an unsupported protocol version', () => {
    vi.useFakeTimers();
    const { socket, onError, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);
    vi.advanceTimersByTime(20_000);

    socket.message({ type: 'market_data.pong', version: 2 });

    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0].message).toMatch(/unexpected or invalid.*pong/i);
    expect(connection.state).toBe('closed');
    expect(socket.closed[0].code).toBe(1011);
  });

  it('fails closed when a heartbeat pong is not received before its timeout', () => {
    vi.useFakeTimers();
    const { socket, onError, connection } = setup();
    socket.readyState = 1;
    socket.emit('open', new Event('open'));
    socket.message({ type: 'market_data.status', version: 1 });
    socket.message(snapshot);

    vi.advanceTimersByTime(30_000);
    expect(onError).toHaveBeenCalledOnce();
    expect(onError.mock.calls[0][0].message).toMatch(/heartbeat pong timed out/i);
    expect(connection.state).toBe('closed');
    expect(socket.closed[0].code).toBe(1011);
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
      ticket: 'ws-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
      getRenewalTicket: async () => 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890',
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
