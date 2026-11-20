import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  requestOhlcvWebSocketTicket,
  WEBSOCKET_TICKET_REQUEST_TIMEOUT_MS,
} from './ohlcvWebSocketTicket';

const validTicket = 'renewed-ticket-abcdefghijklmnopqrstuvwxyz1234567890';
const validPayload = { ticket: validTicket, purpose: 'market-data', expiresIn: 90 };

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn());
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe('requestOhlcvWebSocketTicket', () => {
  it('posts the Firebase bearer token over the normalized HTTPS endpoint without caching or redirects', async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify(validPayload), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    }));

    await expect(requestOhlcvWebSocketTicket(
      'https://market.example.test/api/?discard=1#fragment',
      'firebase-id-token',
    )).resolves.toBe(validTicket);

    expect(fetch).toHaveBeenCalledOnce();
    const [url, init] = vi.mocked(fetch).mock.calls[0];
    expect(url).toBe('https://market.example.test/v1/auth/websocket-ticket');
    expect(init).toMatchObject({
      method: 'POST',
      headers: { Authorization: 'Bearer firebase-id-token' },
      cache: 'no-store',
      credentials: 'omit',
      redirect: 'error',
    });
    expect(init?.signal).toBeInstanceOf(AbortSignal);
  });

  it('preserves the authentication-expired signal for the reconnect supervisor', async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(null, { status: 401 }));
    const error = await requestOhlcvWebSocketTicket(
      'https://market.example.test',
      'firebase-id-token',
    ).catch((value: Error & { status?: number }) => value);

    expect(error).toMatchObject({ status: 401 });
    expect(error.message).toMatch(/authentication was rejected/i);
  });

  it('aborts a request that never receives response headers at the hard deadline', async () => {
    vi.useFakeTimers();
    vi.mocked(fetch).mockImplementation((_input, init) => new Promise((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    }));

    const pending = requestOhlcvWebSocketTicket(
      'https://market.example.test',
      'firebase-id-token',
    );
    await vi.advanceTimersByTimeAsync(WEBSOCKET_TICKET_REQUEST_TIMEOUT_MS);
    await expect(pending).rejects.toThrow(/request timed out/i);
    expect(vi.mocked(fetch).mock.calls[0][1]?.signal?.aborted).toBe(true);
  });

  it('keeps the same deadline active while reading the response body', async () => {
    vi.useFakeTimers();
    vi.mocked(fetch).mockImplementation((_input, init) => Promise.resolve({
      status: 200,
      ok: true,
      json: () => new Promise((_resolve, reject) => {
        init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
      }),
    } as Response));

    const pending = requestOhlcvWebSocketTicket(
      'https://market.example.test',
      'firebase-id-token',
    );
    await vi.advanceTimersByTimeAsync(WEBSOCKET_TICKET_REQUEST_TIMEOUT_MS);
    await expect(pending).rejects.toThrow(/request timed out/i);
  });

  it('rejects malformed ticket payloads and never returns an unvalidated ticket', async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify({
      ticket: validTicket,
      purpose: 'other-purpose',
      expiresIn: 90,
    }), { status: 200 }));

    await expect(requestOhlcvWebSocketTicket(
      'https://market.example.test',
      'firebase-id-token',
    )).rejects.toThrow(/failed validation/i);
  });

  it('rejects missing credentials and URLs with embedded credentials before making a request', async () => {
    await expect(requestOhlcvWebSocketTicket('https://market.example.test', ' '))
      .rejects.toThrow(/identity token is required/i);
    await expect(requestOhlcvWebSocketTicket('https://user:pass@market.example.test', 'token'))
      .rejects.toThrow(/without embedded credentials/i);
    expect(fetch).not.toHaveBeenCalled();
  });
});
