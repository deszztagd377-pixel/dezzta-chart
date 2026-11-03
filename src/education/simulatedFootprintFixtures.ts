import type { SimulatedTradeEvent } from './simulatedFootprint';

/**
 * Fixed, reproducible educational event tape.
 * Values are arbitrary simulation units and are not market observations.
 */
export const simulatedFootprintTape: readonly SimulatedTradeEvent[] = [
  { eventId: 'fixture-001', timestampMs: 1_000, priceTicks: 100, quantity: 3, aggressorSide: 'buy' },
  { eventId: 'fixture-002', timestampMs: 1_180, priceTicks: 100, quantity: 2, aggressorSide: 'sell' },
  { eventId: 'fixture-003', timestampMs: 1_420, priceTicks: 101, quantity: 4, aggressorSide: 'buy' },
  { eventId: 'fixture-004', timestampMs: 1_760, priceTicks: 100, quantity: 1, aggressorSide: 'unknown' },
  { eventId: 'fixture-005', timestampMs: 2_030, priceTicks: 101, quantity: 5, aggressorSide: 'sell' },
  { eventId: 'fixture-006', timestampMs: 2_510, priceTicks: 100, quantity: 2, aggressorSide: 'buy' },
  { eventId: 'fixture-007', timestampMs: 2_900, priceTicks: 102, quantity: 6, aggressorSide: 'unknown' },
  { eventId: 'fixture-008', timestampMs: 3_150, priceTicks: 101, quantity: 3, aggressorSide: 'buy' },
];

/** Returns a defensive copy so tests cannot mutate the shared fixture. */
export function createSimulatedFootprintTape(): SimulatedTradeEvent[] {
  return simulatedFootprintTape.map((event) => ({ ...event }));
}

/**
 * Returns a deterministic prefix of the tape, useful for stepping through
 * one event at a time in tests. It deliberately does not create timers.
 */
export function getSimulatedFootprintStep(
  step: number,
): SimulatedTradeEvent | null {
  if (!Number.isSafeInteger(step) || step < 0) return null;
  const event = simulatedFootprintTape[step];
  return event ? { ...event } : null;
}
