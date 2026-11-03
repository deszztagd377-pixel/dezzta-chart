import { describe, expect, it } from 'vitest';
import { SimulatedFootprintAccumulator } from './simulatedFootprint';

describe('SimulatedFootprintAccumulator', () => {
  it('updates a one-second price cell immediately for every accepted event', () => {
    const footprint = new SimulatedFootprintAccumulator(1);

    expect(footprint.ingest({
      eventId: 'sim-1', timestampMs: 1_250, priceTicks: 100, quantity: 4,
      aggressorSide: 'buy',
    })).toEqual({ status: 'accepted', bucketStartMs: 1_000 });

    expect(footprint.snapshot().cells).toEqual([{
      bucketStartMs: 1_000,
      priceTicks: 100,
      buyVolume: 4,
      sellVolume: 0,
      unknownVolume: 0,
      delta: 4,
      eventCount: 1,
    }]);

    footprint.ingest({
      eventId: 'sim-2', timestampMs: 1_800, priceTicks: 100, quantity: 3,
      aggressorSide: 'sell',
    });

    expect(footprint.snapshot().cells[0]).toMatchObject({
      buyVolume: 4, sellVolume: 3, unknownVolume: 0, delta: 1, eventCount: 2,
    });
  });

  it('uses event time, not arrival order, for late and out-of-order events', () => {
    const footprint = new SimulatedFootprintAccumulator(1);
    footprint.ingest({
      eventId: 'later-first', timestampMs: 3_100, priceTicks: 101, quantity: 2,
      aggressorSide: 'buy',
    });
    footprint.ingest({
      eventId: 'late-arrival', timestampMs: 1_900, priceTicks: 101, quantity: 5,
      aggressorSide: 'sell',
    });

    expect(footprint.snapshot().cells.map((cell) => cell.bucketStartMs)).toEqual([
      1_000, 3_000,
    ]);
    expect(footprint.snapshot().cells[0].sellVolume).toBe(5);
  });

  it('aggregates into a larger interval without losing per-price cells', () => {
    const footprint = new SimulatedFootprintAccumulator(5);
    footprint.ingest({
      eventId: 'a', timestampMs: 1_100, priceTicks: 100, quantity: 2,
      aggressorSide: 'buy',
    });
    footprint.ingest({
      eventId: 'b', timestampMs: 4_900, priceTicks: 101, quantity: 7,
      aggressorSide: 'unknown',
    });
    footprint.ingest({
      eventId: 'c', timestampMs: 5_000, priceTicks: 100, quantity: 3,
      aggressorSide: 'sell',
    });

    const snapshot = footprint.snapshot();
    expect(snapshot.intervalSeconds).toBe(5);
    expect(snapshot.cells.map((cell) => cell.bucketStartMs)).toEqual([0, 0, 5_000]);
    expect(snapshot.cells[0].priceTicks).toBe(101);
    expect(snapshot.cells[0].unknownVolume).toBe(7);
  });

  it('deduplicates event IDs and does not double-count replays', () => {
    const footprint = new SimulatedFootprintAccumulator(1);
    const event = {
      eventId: 'same-id', timestampMs: 2_000, priceTicks: 99, quantity: 6,
      aggressorSide: 'buy' as const,
    };

    expect(footprint.ingest(event).status).toBe('accepted');
    expect(footprint.ingest(event)).toEqual({ status: 'duplicate' });
    expect(footprint.snapshot().cells[0].buyVolume).toBe(6);
    expect(footprint.snapshot().cells[0].eventCount).toBe(1);
  });

  it('keeps unknown aggressor volume separate instead of guessing a side', () => {
    const footprint = new SimulatedFootprintAccumulator(1);
    footprint.ingest({
      eventId: 'unknown', timestampMs: 0, priceTicks: 50, quantity: 9,
      aggressorSide: 'unknown',
    });

    expect(footprint.snapshot().cells[0]).toMatchObject({
      buyVolume: 0, sellVolume: 0, unknownVolume: 9, delta: 0,
    });
  });

  it('rejects invalid events and fails closed when the dedupe ledger is full', () => {
    const footprint = new SimulatedFootprintAccumulator(1, 1);
    expect(footprint.ingest({
      eventId: 'bad', timestampMs: 0, priceTicks: 1, quantity: 0,
      aggressorSide: 'buy',
    })).toMatchObject({ status: 'invalid' });

    const valid = {
      eventId: 'first', timestampMs: 0, priceTicks: 1, quantity: 1,
      aggressorSide: 'buy' as const,
    };
    expect(footprint.ingest(valid).status).toBe('accepted');
    expect(footprint.ingest({
      ...valid, eventId: 'second',
    })).toEqual({ status: 'capacity_exceeded' });
    expect(footprint.snapshot().cells).toHaveLength(1);
  });

  it('clears cells and replay IDs on reset', () => {
    const footprint = new SimulatedFootprintAccumulator(1);
    const event = {
      eventId: 'reusable', timestampMs: 0, priceTicks: 1, quantity: 2,
      aggressorSide: 'buy' as const,
    };
    footprint.ingest(event);
    footprint.reset();

    expect(footprint.snapshot().cells).toEqual([]);
    expect(footprint.ingest(event).status).toBe('accepted');
  });

  it('marks every snapshot as simulated', () => {
    expect(new SimulatedFootprintAccumulator().snapshot().dataOrigin).toBe('SIMULATED');
  });
});
