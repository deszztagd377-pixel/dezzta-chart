export type OhlcvStreamLifecycleReason = 'active' | 'offline' | 'hidden';

export interface OhlcvStreamLifecycle {
  readonly online: boolean;
  readonly visible: boolean;
  readonly shouldConnect: boolean;
  readonly reason: OhlcvStreamLifecycleReason;
}

/**
 * Browser lifecycle policy for the authenticated OHLCV stream.
 * A hidden or offline page must not keep a reconnect loop alive; returning to
 * the foreground while online creates a new supervisor and requests a fresh
 * snapshot instead of trusting a backgrounded transport.
 */
export function getOhlcvStreamLifecycle(
  online: boolean,
  visibilityState: string,
): OhlcvStreamLifecycle {
  const visible = visibilityState === 'visible';
  const reason: OhlcvStreamLifecycleReason = !online
    ? 'offline'
    : !visible ? 'hidden' : 'active';

  return Object.freeze({
    online,
    visible,
    shouldConnect: online && visible,
    reason,
  });
}
