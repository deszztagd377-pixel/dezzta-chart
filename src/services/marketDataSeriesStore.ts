import type { ChartData } from '../types';
import {
  getMarketSeriesIdentityKey,
  validateMarketDataBars,
  validateMarketSeriesIdentity,
  type MarketDataSnapshot,
  type MarketDataStatus,
  type MarketSeriesIdentity,
} from './marketDataStore';

interface SeriesEntry {
  snapshot: MarketDataSnapshot;
  listeners: Set<() => void>;
}

export interface PublishSeriesSnapshotInput {
  identity: MarketSeriesIdentity;
  status: MarketDataStatus;
  bars?: readonly ChartData[];
  detail?: string | null;
}

/**
 * Keyed immutable snapshot store for independent chart panels.
 *
 * This store is deliberately transport-agnostic: it does not open sockets,
 * acquire provider subscriptions, or imply upstream provider demand. A future
 * supervisor can publish validated per-series events here without allowing
 * one chart's selection or cleanup to overwrite another chart's snapshot.
 */
export class MarketDataSeriesStore {
  private readonly entries = new Map<string, SeriesEntry>();

  private readonly maxSeriesEntries: number;

  constructor(maxSeriesEntries = 32) {
    if (!Number.isSafeInteger(maxSeriesEntries) || maxSeriesEntries < 1) {
      throw new Error('Market-data series store capacity must be a positive safe integer.');
    }
    this.maxSeriesEntries = maxSeriesEntries;
  }

  private getEntry(identity: MarketSeriesIdentity): SeriesEntry {
    validateMarketSeriesIdentity(identity);
    const key = getMarketSeriesIdentityKey(identity);
    let entry = this.entries.get(key);
    if (entry) {
      // Map insertion order is the deterministic least-recently-used order.
      this.entries.delete(key);
      this.entries.set(key, entry);
      return entry;
    }

    if (this.entries.size >= this.maxSeriesEntries) {
      const evictable = [...this.entries.entries()].find(([, candidate]) => candidate.listeners.size === 0);
      if (!evictable) {
        throw new Error('Market-data series store capacity is exhausted by active chart subscribers.');
      }
      this.entries.delete(evictable[0]);
    }

    if (!entry) {
      const frozenIdentity = Object.freeze({ ...identity });
      const snapshot: MarketDataSnapshot = Object.freeze({
        identity: frozenIdentity,
        status: 'loading',
        source: 'none',
        bars: Object.freeze([]),
        detail: 'No snapshot has been published for this series.',
        revision: 0,
        lastChange: Object.freeze({ type: 'snapshot' }),
      });
      entry = { snapshot, listeners: new Set() };
      this.entries.set(key, entry);
    }
    return entry;
  }

  getSnapshot(identity: MarketSeriesIdentity): MarketDataSnapshot {
    return this.getEntry(identity).snapshot;
  }

  subscribe(identity: MarketSeriesIdentity, listener: () => void): () => void {
    const entry = this.getEntry(identity);
    entry.listeners.add(listener);
    let subscribed = true;
    return () => {
      if (!subscribed) return;
      subscribed = false;
      entry.listeners.delete(listener);
    };
  }

  publishSnapshot(input: PublishSeriesSnapshotInput): void {
    const entry = this.getEntry(input.identity);
    const bars = input.bars ?? [];
    const backendState = input.status === 'ready' || input.status === 'degraded';

    if (backendState && bars.length === 0) {
      throw new Error('Backend market data cannot be ready without validated bars.');
    }
    if (!backendState && bars.length > 0) {
      throw new Error('Non-ready market-data states cannot publish indicator bars.');
    }
    if (backendState) validateMarketDataBars(bars);

    const immutableBars = Object.freeze(
      bars.map((bar) => Object.freeze({ ...bar })),
    );
    entry.snapshot = Object.freeze({
      identity: Object.freeze({ ...input.identity }),
      status: input.status,
      source: backendState ? 'backend' : input.status === 'demo' ? 'demo' : 'none',
      bars: immutableBars,
      detail: input.detail ?? null,
      revision: entry.snapshot.revision + 1,
      lastChange: Object.freeze({ type: 'snapshot' }),
    });
    this.emit(entry);
  }

  publishUpdate(input: { identity: MarketSeriesIdentity; bar: ChartData }): void {
    const entry = this.getEntry(input.identity);
    const current = entry.snapshot;
    if (
      current.source !== 'backend' ||
      (current.status !== 'ready' && current.status !== 'degraded')
    ) {
      throw new Error('Incremental updates require an active backend snapshot for this series.');
    }

    validateMarketDataBars([input.bar]);
    const nextBars = [...current.bars];
    let low = 0;
    let high = nextBars.length;
    while (low < high) {
      const middle = low + Math.floor((high - low) / 2);
      if (nextBars[middle].timestamp < input.bar.timestamp) low = middle + 1;
      else high = middle;
    }

    if (low < nextBars.length && nextBars[low].timestamp === input.bar.timestamp) {
      nextBars[low] = input.bar;
    } else {
      nextBars.splice(low, 0, input.bar);
    }
    validateMarketDataBars(nextBars);

    entry.snapshot = Object.freeze({
      ...current,
      bars: Object.freeze(nextBars.map((bar) => Object.freeze({ ...bar }))),
      revision: current.revision + 1,
      lastChange: Object.freeze({
        type: 'update',
        bar: Object.freeze({ ...input.bar }),
      }),
    });
    this.emit(entry);
  }

  reset(identity: MarketSeriesIdentity, status: MarketDataStatus, detail: string | null): void {
    this.publishSnapshot({ identity, status, bars: [], detail });
  }

  getSeriesCount(): number {
    return this.entries.size;
  }

  getCapacity(): number {
    return this.maxSeriesEntries;
  }

  getSubscriberCount(identity: MarketSeriesIdentity): number {
    return this.getEntry(identity).listeners.size;
  }

  private emit(entry: SeriesEntry): void {
    for (const listener of [...entry.listeners]) {
      try {
        listener();
      } catch {
        // One chart observer must not prevent other panels receiving updates.
      }
    }
  }
}

/** Shared keyed store; legacy single-chart consumers remain on marketDataStore until migrated. */
export const marketDataSeriesStore = new MarketDataSeriesStore();
