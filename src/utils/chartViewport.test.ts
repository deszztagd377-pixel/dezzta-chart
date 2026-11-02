import { describe, expect, it } from 'vitest';
import { getMeasurableChartSize } from './chartViewport';

describe('chart viewport measurement', () => {
  it('returns positive finite dimensions unchanged', () => {
    expect(getMeasurableChartSize({ width: 360, height: 520 })).toEqual({
      width: 360,
      height: 520,
    });
  });

  it('rejects a zero-width container', () => {
    expect(getMeasurableChartSize({ width: 0, height: 520 })).toBeNull();
  });

  it('rejects a zero-height container', () => {
    expect(getMeasurableChartSize({ width: 360, height: 0 })).toBeNull();
  });

  it('rejects negative dimensions', () => {
    expect(getMeasurableChartSize({ width: -1, height: 520 })).toBeNull();
    expect(getMeasurableChartSize({ width: 360, height: -1 })).toBeNull();
  });

  it('rejects non-finite dimensions', () => {
    expect(getMeasurableChartSize({ width: Number.NaN, height: 520 })).toBeNull();
    expect(getMeasurableChartSize({ width: 360, height: Number.POSITIVE_INFINITY })).toBeNull();
  });
});
