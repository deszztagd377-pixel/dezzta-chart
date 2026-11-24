import {
  getMarketSeriesIdentityKey,
  validateMarketSeriesIdentity,
  type MarketSeriesIdentity,
} from './marketDataStore';
import {
  startOhlcvStreamSupervisor,
  type OhlcvStreamSupervisor,
  type OhlcvStreamSupervisorOptions,
  type OhlcvSupervisorStatus,
} from './ohlcvStreamSupervisor';

interface OwnerCallbacks {
  onStatus?: (status: OhlcvSupervisorStatus) => void;
  onError?: (error: Error) => void;
}

interface SeriesEntry {
  identity: Readonly<MarketSeriesIdentity>;
  baseUrl: string;
  canonicalInstrumentId: string;
  supervisor: OhlcvStreamSupervisor;
  nextGeneration: number;
  owners: Map<string, { generation: number; callbacks: OwnerCallbacks }>;
}

export interface OhlcvSeriesSupervisorLease {
  readonly key: string;
  readonly ownerId: string;
  readonly generation: number;
  release(): void;
}

/**
 * Shares one authenticated WebSocket supervisor per canonical market series.
 * Panel ownership is reference-counted; only the final owner closes transport.
 * Each series writes only to the keyed market-data store.
 */
export class OhlcvSeriesSupervisorRegistry {
  private readonly entries = new Map<string, SeriesEntry>();

  constructor(private readonly maxActiveSeries = 32) {
    if (!Number.isSafeInteger(maxActiveSeries) || maxActiveSeries < 1) {
      throw new Error('OHLCV active-series capacity must be a positive safe integer.');
    }
  }

  acquire(
    options: OhlcvStreamSupervisorOptions,
    ownerId: string,
  ): OhlcvSeriesSupervisorLease {
    validateMarketSeriesIdentity(options.identity);
    if (typeof ownerId !== 'string' || !ownerId.trim()) {
      throw new Error('OHLCV panel owner ID must be a non-empty string.');
    }
    const normalizedOwnerId = ownerId.trim();
    const key = getMarketSeriesIdentityKey(options.identity);
    let entry = this.entries.get(key);

    if (entry && (
      entry.baseUrl !== options.baseUrl ||
      entry.canonicalInstrumentId !== options.canonicalInstrumentId
    )) {
      throw new Error(
        'OHLCV series identity is already owned by a different transport endpoint or canonical instrument mapping.',
      );
    }

    if (!entry && this.entries.size >= this.maxActiveSeries) {
      throw new Error(`OHLCV active-series capacity (${this.maxActiveSeries}) is exhausted.`);
    }

    if (!entry) {
      const owners = new Map<string, { generation: number; callbacks: OwnerCallbacks }>();
      const { onStatus, onError, ...supervisorOptions } = options;
      const supervisor = startOhlcvStreamSupervisor({
        ...supervisorOptions,
        seriesScoped: true,
        onStatus: (status) => {
          for (const owner of [...owners.values()]) {
            try { owner.callbacks.onStatus?.(status); } catch { /* Observer isolation. */ }
          }
        },
        onError: (error) => {
          for (const owner of [...owners.values()]) {
            try { owner.callbacks.onError?.(error); } catch { /* Observer isolation. */ }
          }
        },
      });
      entry = {
        identity: Object.freeze({ ...options.identity }),
        baseUrl: options.baseUrl,
        canonicalInstrumentId: options.canonicalInstrumentId,
        supervisor,
        nextGeneration: 0,
        owners,
      };
      this.entries.set(key, entry);
    }

    if (!Number.isSafeInteger(entry.nextGeneration + 1)) {
      throw new Error('OHLCV series owner generation exhausted its safe integer range.');
    }
    const generation = ++entry.nextGeneration;
    entry.owners.set(normalizedOwnerId, {
      generation,
      callbacks: { onStatus: options.onStatus, onError: options.onError },
    });
    // A panel joining an already-running series must receive its current state
    // immediately; otherwise its UI can remain "connecting" until the next tick.
    try { options.onStatus?.(entry.supervisor.status); } catch { /* Observer isolation. */ }

    let released = false;
    return Object.freeze({
      key,
      ownerId: normalizedOwnerId,
      generation,
      release: () => {
        if (released) return;
        released = true;
        const current = this.entries.get(key);
        const owner = current?.owners.get(normalizedOwnerId);
        if (!current || !owner || owner.generation !== generation) return;
        current.owners.delete(normalizedOwnerId);
        if (current.owners.size > 0) return;
        this.entries.delete(key);
        current.supervisor.stop();
      },
    });
  }

  getOwnerCount(identity: MarketSeriesIdentity): number {
    validateMarketSeriesIdentity(identity);
    return this.entries.get(getMarketSeriesIdentityKey(identity))?.owners.size ?? 0;
  }

  getSeriesCount(): number {
    return this.entries.size;
  }

  getCapacity(): number {
    return this.maxActiveSeries;
  }

  getStatus(identity: MarketSeriesIdentity): OhlcvSupervisorStatus | 'stopped' {
    validateMarketSeriesIdentity(identity);
    return this.entries.get(getMarketSeriesIdentityKey(identity))?.supervisor.status ?? 'stopped';
  }
}

export const ohlcvSeriesSupervisorRegistry = new OhlcvSeriesSupervisorRegistry();
