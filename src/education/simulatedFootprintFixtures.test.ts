import { describe, expect, it } from 'vitest';
import {
  createSimulatedFootprintTape,
  getSimulatedFootprintStep,
  simulatedFootprintTape,
} from './simulatedFootprintFixtures';

describe('simulatedFootprintFixtures', () => {
  it('provides a stable, ordered educational event tape', () => {
    const tape = createSimulatedFootprintTape();
    expect(tape).toHaveLength(8);
    expect(tape.map((event) => event.timestampMs)).toEqual([
      1_000, 1_180, 1_420, 1_760, 2_030, 2_510, 2_900, 3_150,
    ]);
    expect(tape.every((event) => event.eventId.startsWith('fixture-'))).toBe(true);
  });

  it('returns one defensive event per requested step', () => {
    const first = getSimulatedFootprintStep(0);
    expect(first).toEqual(simulatedFootprintTape[0]);
    if (first) first.quantity = 999;
    expect(getSimulatedFootprintStep(0)?.quantity).toBe(3);
    expect(getSimulatedFootprintStep(8)).toBeNull();
  });

  it('rejects invalid step indexes without throwing', () => {
    expect(getSimulatedFootprintStep(-1)).toBeNull();
    expect(getSimulatedFootprintStep(1.5)).toBeNull();
    expect(getSimulatedFootprintStep(Number.NaN)).toBeNull();
  });

  it('keeps fixture copies isolated from the exported source tape', () => {
    const copy = createSimulatedFootprintTape();
    copy[0].eventId = 'mutated';
    expect(simulatedFootprintTape[0].eventId).toBe('fixture-001');
  });
});
