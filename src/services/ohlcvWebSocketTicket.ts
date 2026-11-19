/** Exchange Firebase credentials over HTTPS; never put the ID token in a WSS frame or URL. */
export async function requestOhlcvWebSocketTicket(baseUrl: string, idToken: string): Promise<string> {
  if (typeof idToken !== 'string' || !idToken.trim()) throw new Error('A Firebase identity token is required.');
  let endpoint: URL;
  try { endpoint = new URL(baseUrl); } catch { throw new Error('Market-data backend URL is invalid.'); }
  if (!['http:', 'https:'].includes(endpoint.protocol) || endpoint.username || endpoint.password) {
    throw new Error('Market-data backend URL must use HTTP(S) without embedded credentials.');
  }
  endpoint.pathname = '/v1/auth/websocket-ticket';
  endpoint.search = '';
  endpoint.hash = '';
  const response = await fetch(endpoint.toString(), {
    method: 'POST',
    headers: { Authorization: `Bearer ${idToken}` },
    cache: 'no-store',
    credentials: 'omit',
    redirect: 'error',
  });
  if (response.status === 401) {
    const error = new Error('Firebase authentication was rejected during WebSocket ticket renewal.') as Error & { status?: number };
    error.status = 401;
    throw error;
  }
  if (!response.ok) throw new Error('The market-data WebSocket ticket service is temporarily unavailable.');
  let payload: unknown;
  try { payload = await response.json(); } catch { throw new Error('The market-data WebSocket ticket response is invalid.'); }
  if (
    typeof payload !== 'object' || payload === null || Array.isArray(payload) ||
    typeof (payload as Record<string, unknown>).ticket !== 'string' ||
    ((payload as Record<string, unknown>).ticket as string).length < 40 ||
    ((payload as Record<string, unknown>).ticket as string).length > 128 ||
    (payload as Record<string, unknown>).purpose !== 'market-data' ||
    (payload as Record<string, unknown>).expiresIn !== 90
  ) throw new Error('The market-data WebSocket ticket response failed validation.');
  return (payload as Record<string, string>).ticket;
}
