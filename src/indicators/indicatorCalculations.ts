import type { ChartData } from '../types';

export interface MacdPoint {
  macd: number | null;
  signal: number | null;
  histogram: number | null;
}

export interface BollingerPoint {
  middle: number | null;
  upper: number | null;
  lower: number | null;
}

function validatePeriod(period: number): void {
  if (!Number.isSafeInteger(period) || period < 1) {
    throw new Error('Indicator period must be a positive safe integer.');
  }
}

function closes(bars: readonly ChartData[]): number[] {
  return bars.map((bar, index) => {
    if (!Number.isFinite(bar.close)) {
      throw new Error(`Bar ${index} has a non-finite close value.`);
    }
    return bar.close;
  });
}

export function calculateSma(values: readonly number[], period: number): Array<number | null> {
  validatePeriod(period);
  const output: Array<number | null> = Array(values.length).fill(null);
  let sum = 0;
  for (let index = 0; index < values.length; index += 1) {
    if (!Number.isFinite(values[index])) throw new Error(`Input ${index} is not finite.`);
    sum += values[index];
    if (index >= period) sum -= values[index - period];
    if (index >= period - 1) output[index] = sum / period;
  }
  return output;
}

export function calculateEma(values: readonly number[], period: number): Array<number | null> {
  validatePeriod(period);
  const output: Array<number | null> = Array(values.length).fill(null);
  if (values.length < period) return output;
  const seed = values.slice(0, period);
  if (seed.some((value) => !Number.isFinite(value))) {
    throw new Error('EMA input contains a non-finite value.');
  }
  let previous = seed.reduce((sum, value) => sum + value, 0) / period;
  output[period - 1] = previous;
  const multiplier = 2 / (period + 1);
  for (let index = period; index < values.length; index += 1) {
    const value = values[index];
    if (!Number.isFinite(value)) throw new Error(`Input ${index} is not finite.`);
    previous = (value - previous) * multiplier + previous;
    output[index] = previous;
  }
  return output;
}

export function calculateRsi(values: readonly number[], period = 14): Array<number | null> {
  validatePeriod(period);
  const output: Array<number | null> = Array(values.length).fill(null);
  if (values.length <= period) return output;

  let gains = 0;
  let losses = 0;
  for (let index = 1; index <= period; index += 1) {
    const change = values[index] - values[index - 1];
    if (!Number.isFinite(change)) throw new Error('RSI input contains a non-finite value.');
    gains += Math.max(change, 0);
    losses += Math.max(-change, 0);
  }

  let averageGain = gains / period;
  let averageLoss = losses / period;
  const toRsi = () => averageLoss === 0
    ? (averageGain === 0 ? 50 : 100)
    : 100 - (100 / (1 + averageGain / averageLoss));
  output[period] = toRsi();

  for (let index = period + 1; index < values.length; index += 1) {
    const change = values[index] - values[index - 1];
    if (!Number.isFinite(change)) throw new Error('RSI input contains a non-finite value.');
    averageGain = (averageGain * (period - 1) + Math.max(change, 0)) / period;
    averageLoss = (averageLoss * (period - 1) + Math.max(-change, 0)) / period;
    output[index] = toRsi();
  }
  return output;
}

export function calculateMacd(
  values: readonly number[],
  fastPeriod = 12,
  slowPeriod = 26,
  signalPeriod = 9,
): MacdPoint[] {
  validatePeriod(fastPeriod);
  validatePeriod(slowPeriod);
  validatePeriod(signalPeriod);
  if (fastPeriod >= slowPeriod) throw new Error('MACD fast period must be smaller than slow period.');

  const fast = calculateEma(values, fastPeriod);
  const slow = calculateEma(values, slowPeriod);
  const macdValues: number[] = [];
  const macdIndices: number[] = [];
  for (let index = 0; index < values.length; index += 1) {
    if (fast[index] !== null && slow[index] !== null) {
      macdValues.push(fast[index]! - slow[index]!);
      macdIndices.push(index);
    }
  }
  const signalValues = calculateEma(macdValues, signalPeriod);
  const output: MacdPoint[] = Array.from({ length: values.length }, () => ({
    macd: null, signal: null, histogram: null,
  }));
  macdIndices.forEach((originalIndex, position) => {
    const macd = macdValues[position];
    const signal = signalValues[position];
    output[originalIndex] = {
      macd,
      signal,
      histogram: signal === null ? null : macd - signal,
    };
  });
  return output;
}

export function calculateBollingerBands(
  values: readonly number[],
  period = 20,
  standardDeviations = 2,
): BollingerPoint[] {
  validatePeriod(period);
  if (!Number.isFinite(standardDeviations) || standardDeviations < 0) {
    throw new Error('Bollinger standard deviation multiplier must be non-negative.');
  }
  const output: BollingerPoint[] = Array.from({ length: values.length }, () => ({
    middle: null, upper: null, lower: null,
  }));
  for (let index = period - 1; index < values.length; index += 1) {
    const window = values.slice(index - period + 1, index + 1);
    if (window.some((value) => !Number.isFinite(value))) {
      throw new Error('Bollinger input contains a non-finite value.');
    }
    const mean = window.reduce((sum, value) => sum + value, 0) / period;
    const variance = window.reduce((sum, value) => sum + ((value - mean) ** 2), 0) / period;
    const deviation = Math.sqrt(variance);
    output[index] = {
      middle: mean,
      upper: mean + standardDeviations * deviation,
      lower: mean - standardDeviations * deviation,
    };
  }
  return output;
}

export function calculateIndicators(bars: readonly ChartData[]) {
  const close = closes(bars);
  return {
    sma20: calculateSma(close, 20),
    ema20: calculateEma(close, 20),
    rsi14: calculateRsi(close, 14),
    macd: calculateMacd(close),
    bollinger20: calculateBollingerBands(close, 20, 2),
  };
}
