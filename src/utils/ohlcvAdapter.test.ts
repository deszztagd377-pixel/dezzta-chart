import { describe, expect, it } from 'vitest';
import { parseOhlcvSnapshot, toChartCandles } from './ohlcvAdapter';

const baseBar = {
  dataset: 'GLBX.MDP3',
  provider: 'databento',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'ESZ6',
  seriesType: 'contract',
  timeframe: '1s',
  tsStartNs: '1793577600000000000',
  open: '6000.125',
  high: '6001.250',
  low: '5999.875',
  close: '6000.750',
  volume: '12',
  tsEventNs: '1793577600999000000',
  tsReceivedNs: '1793577601000000000',
  sequence: 7,
  sequenceOrigin: 'local',
  origin: 'provider',
  completeness: 'complete',
};

const makeSnapshot = (overrides: Record<string, unknown> = {}) => ({
  type: 'market_data.ohlcv.snapshot',
  version: 1,
  state: 'ready',
  feedState: 'live',
  timestampUnit: 'nanoseconds',
  priceRepresentation: 'decimal-string',
  count: 1,
  truncated: false,
  bars: [{ ...baseBar }],
  detail: null,
  ...overrides,
});

const identity = {
  dataset: 'GLBX.MDP3',
  publisherId: 1,
  instrumentId: 123,
  rawSymbol: 'ESZ6',
  timeframe: '1s' as const,
};

describe('parseOhlcvSnapshot', () => {
  it('accepts a valid versioned snapshot while preserving decimal strings', () => {
    const result = parseOhlcvSnapshot(makeSnapshot());
    expect(result.bars[0].open).toBe('6000.125');
    expect(result.bars[0].tsStartNs).toBe('1793577600000000000');
  });

  it('rejects unsupported message versions', () => {
    expect(() => parseOhlcvSnapshot(makeSnapshot({ version: 2 }))).toThrow(/version/);
  });

  it('rejects malformed decimal values', () => {
    const payload = makeSnapshot({ bars: [{ ...baseBar, close: 'NaN' }] });
    expect(() => parseOhlcvSnapshot(payload)).toThrow(/decimal close/);
  });

  it('rejects invalid OHLC boundaries', () => {
    const payload = makeSnapshot({ bars: [{ ...baseBar, high: '5998' }] });
    expect(() => parseOhlcvSnapshot(payload)).toThrow(/boundaries/);
  });

  it('rejects negative volume', () => {
    const payload = makeSnapshot({ bars: [{ ...baseBar, volume: '-1' }] });
    expect(() => parseOhlcvSnapshot(payload)).toThrow(/boundaries/);
  });

  it('checks OHLC boundaries without rounding high-precision decimals', () => {
    const payload = makeSnapshot({
      bars: [{
        ...baseBar,
        open: '6000.125000000000000001',
        high: '6000.125000000000000000',
        low: '5999.875',
        close: '6000.100',
      }],
    });
    expect(() => parseOhlcvSnapshot(payload)).toThrow(/boundaries/);
  });

  it('rejects non-chronological and duplicate timestamps', () => {
    const payload = makeSnapshot({
      bars: [
        { ...baseBar },
        { ...baseBar, tsStartNs: '1793577600000000000' },
      ],
    });
    expect(() => parseOhlcvSnapshot(payload)).toThrow(/chronological/);
  });
});

describe('toChartCandles', () => {
  it('converts nanoseconds and decimals only at the chart boundary', () => {
    const snapshot = parseOhlcvSnapshot(makeSnapshot());
    const candles = toChartCandles(snapshot, identity);
    expect(candles).toEqual([{
      timestamp: 1793577600,
      open: 6000.125,
      high: 6001.25,
      low: 5999.875,
      close: 6000.75,
      volume: 12,
    }]);
  });

  it('does not mix bars from another instrument or timeframe', () => {
    const payload = makeSnapshot({
      bars: [
        { ...baseBar },
        { ...baseBar, instrumentId: 456 },
        { ...baseBar, timeframe: '5s' },
      ],
    });
    const snapshot = parseOhlcvSnapshot(payload);
    expect(toChartCandles(snapshot, identity)).toHaveLength(1);
  });

  it('returns no candles for an unavailable snapshot', () => {
    const snapshot = parseOhlcvSnapshot(makeSnapshot({
      state: 'unavailable',
      bars: [],
      count: 0,
    }));
    expect(toChartCandles(snapshot, identity)).toEqual([]);
  });
});
