/**
 * Deterministic, offline-only Footprint aggregation for education and UI tests.
 * This module accepts synthetic events only; it has no provider/network adapter.
 */

export type SimulatedAggressorSide = 'buy' | 'sell' | 'unknown';

export interface SimulatedTradeEvent {
  eventId: string;
  /** Synthetic event time in Unix milliseconds. */
  timestampMs: number;
  /** Integer price-step index; avoids floating-point price grouping. */
  priceTicks: number;
  /** Positive integer quantity in arbitrary simulation units. */
  quantity: number;
  aggressorSide: SimulatedAggressorSide;
}

export interface SimulatedFootprintCell {
  bucketStartMs: number;
  priceTicks: number;
  buyVolume: number;
  sellVolume: number;
  unknownVolume: number;
  delta: number;
  eventCount: number;
}

export interface SimulatedFootprintSnapshot {
  dataOrigin: 'SIMULATED';
  intervalSeconds: number;
  cells: SimulatedFootprintCell[];
}

export type SimulatedIngestResult =
  | { status: 'accepted'; bucketStartMs: number }
  | { status: 'duplicate' }
  | { status: 'invalid'; reason: string }
  | { status: 'capacity_exceeded' };

const DEFAULT_MAX_UNIQUE_EVENTS = 10_000;

function isSafeInteger(value: number): boolean {
  return Number.isSafeInteger(value);
}

/**
 * Accumulates each synthetic event immediately into its event-time bucket.
 * Late/out-of-order events remain in their original bucket. Duplicate IDs are
 * ignored. The bounded ID ledger fails closed at capacity rather than evicting
 * IDs and potentially counting a replay twice.
 */
export class SimulatedFootprintAccumulator {
  private readonly intervalMs: number;
  private readonly maxUniqueEvents: number;
  private readonly seenEventIds = new Set<string>();
  private readonly cells = new Map<string, SimulatedFootprintCell>();

  constructor(intervalSeconds = 1, maxUniqueEvents = DEFAULT_MAX_UNIQUE_EVENTS) {
    if (!isSafeInteger(intervalSeconds) || intervalSeconds < 1) {
      throw new RangeError('intervalSeconds must be a positive safe integer.');
    }
    if (!isSafeInteger(maxUniqueEvents) || maxUniqueEvents < 1) {
      throw new RangeError('maxUniqueEvents must be a positive safe integer.');
    }
    this.intervalMs = intervalSeconds * 1_000;
    if (!Number.isSafeInteger(this.intervalMs)) {
      throw new RangeError('intervalSeconds is too large.');
    }
    this.maxUniqueEvents = maxUniqueEvents;
  }

  ingest(event: SimulatedTradeEvent): SimulatedIngestResult {
    const invalidReason = this.validate(event);
    if (invalidReason) return { status: 'invalid', reason: invalidReason };

    if (this.seenEventIds.has(event.eventId)) {
      return { status: 'duplicate' };
    }
    if (this.seenEventIds.size >= this.maxUniqueEvents) {
      return { status: 'capacity_exceeded' };
    }

    const bucketStartMs = Math.floor(event.timestampMs / this.intervalMs) * this.intervalMs;
    const key = `${bucketStartMs}:${event.priceTicks}`;
    const current = this.cells.get(key) ?? {
      bucketStartMs,
      priceTicks: event.priceTicks,
      buyVolume: 0,
      sellVolume: 0,
      unknownVolume: 0,
      delta: 0,
      eventCount: 0,
    };

    const next = { ...current, eventCount: current.eventCount + 1 };
    if (event.aggressorSide === 'buy') next.buyVolume += event.quantity;
    else if (event.aggressorSide === 'sell') next.sellVolume += event.quantity;
    else next.unknownVolume += event.quantity;

    next.delta = next.buyVolume - next.sellVolume;
    if (
      !isSafeInteger(next.eventCount) ||
      !isSafeInteger(next.buyVolume) ||
      !isSafeInteger(next.sellVolume) ||
      !isSafeInteger(next.unknownVolume) ||
      !isSafeInteger(next.delta)
    ) {
      return { status: 'invalid', reason: 'Aggregate exceeds safe integer precision.' };
    }

    this.seenEventIds.add(event.eventId);
    this.cells.set(key, next);
    return { status: 'accepted', bucketStartMs };
  }

  snapshot(): SimulatedFootprintSnapshot {
    const cells = [...this.cells.values()]
      .map((cell) => ({ ...cell }))
      .sort((a, b) =>
        a.bucketStartMs - b.bucketStartMs || b.priceTicks - a.priceTicks,
      );

    return {
      dataOrigin: 'SIMULATED',
      intervalSeconds: this.intervalMs / 1_000,
      cells,
    };
  }

  reset(): void {
    this.seenEventIds.clear();
    this.cells.clear();
  }

  private validate(event: SimulatedTradeEvent): string | null {
    if (!event || typeof event !== 'object') return 'Event must be an object.';
    if (typeof event.eventId !== 'string' || event.eventId.trim().length === 0 ||
        event.eventId.length > 128) return 'eventId must contain 1 to 128 characters.';
    if (!isSafeInteger(event.timestampMs) || event.timestampMs < 0) {
      return 'timestampMs must be a non-negative safe integer.';
    }
    if (!isSafeInteger(event.priceTicks)) return 'priceTicks must be a safe integer.';
    if (!isSafeInteger(event.quantity) || event.quantity <= 0) {
      return 'quantity must be a positive safe integer.';
    }
    if (!['buy', 'sell', 'unknown'].includes(event.aggressorSide)) {
      return 'aggressorSide must be buy, sell, or unknown.';
    }
    return null;
  }
}
