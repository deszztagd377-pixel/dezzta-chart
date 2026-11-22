import {
  getMarketSeriesIdentityKey,
  validateMarketSeriesIdentity,
  type MarketSeriesIdentity,
} from './marketDataStore';

interface OwnerLease {
  generation: number;
}

interface SeriesLeaseEntry {
  identity: Readonly<MarketSeriesIdentity>;
  nextGeneration: number;
  owners: Map<string, OwnerLease>;
}

export interface MarketDataSeriesLease {
  readonly key: string;
  readonly ownerId: string;
  readonly generation: number;
  release(): void;
}

/**
 * Tracks chart-panel ownership of a canonical series independently from
 * WebSocket/provider subscriptions. Generation checks make stale React
 * effect cleanups harmless when the same panel reacquires a series.
 *
 * This registry does not create sockets or claim provider-side ref-counting.
 */
export class MarketDataSeriesLeaseRegistry {
  private readonly entries = new Map<string, SeriesLeaseEntry>();

  constructor(
    private readonly onLastOwnerReleased?: (identity: Readonly<MarketSeriesIdentity>) => void,
  ) {}

  acquire(identity: MarketSeriesIdentity, ownerId: string): MarketDataSeriesLease {
    validateMarketSeriesIdentity(identity);
    if (typeof ownerId !== 'string' || ownerId.trim().length === 0) {
      throw new Error('Market-data panel owner ID must be a non-empty string.');
    }
    const normalizedOwnerId = ownerId.trim();

    const key = getMarketSeriesIdentityKey(identity);
    let entry = this.entries.get(key);
    if (!entry) {
      entry = {
        identity: Object.freeze({ ...identity }),
        nextGeneration: 0,
        owners: new Map(),
      };
      this.entries.set(key, entry);
    }

    if (!Number.isSafeInteger(entry.nextGeneration + 1)) {
      throw new Error('Market-data panel lease generation exhausted its safe integer range.');
    }
    const generation = ++entry.nextGeneration;
    // Reacquiring with the same owner ID replaces its generation rather than
    // incrementing the number of unique panels.
    entry.owners.set(normalizedOwnerId, { generation });

    let released = false;
    return Object.freeze({
      key,
      ownerId: normalizedOwnerId,
      generation,
      release: () => {
        if (released) return;
        released = true;

        const currentEntry = this.entries.get(key);
        if (!currentEntry) return;
        const currentOwner = currentEntry.owners.get(normalizedOwnerId);
        if (!currentOwner || currentOwner.generation !== generation) return;

        currentEntry.owners.delete(normalizedOwnerId);
        if (currentEntry.owners.size !== 0) return;

        this.entries.delete(key);
        try {
          this.onLastOwnerReleased?.(currentEntry.identity);
        } catch {
          // Lease cleanup must remain safe inside React effect cleanup.
        }
      },
    });
  }

  getOwnerCount(identity: MarketSeriesIdentity): number {
    validateMarketSeriesIdentity(identity);
    return this.entries.get(getMarketSeriesIdentityKey(identity))?.owners.size ?? 0;
  }

  hasOwner(identity: MarketSeriesIdentity, ownerId: string): boolean {
    validateMarketSeriesIdentity(identity);
    if (typeof ownerId !== 'string' || ownerId.trim().length === 0) return false;
    return this.entries.get(getMarketSeriesIdentityKey(identity))?.owners.has(ownerId.trim()) ?? false;
  }

  getSeriesCount(): number {
    return this.entries.size;
  }
}

/** Shared registry for chart-panel leases; transport ownership is integrated separately. */
export const marketDataSeriesLeaseRegistry = new MarketDataSeriesLeaseRegistry();
