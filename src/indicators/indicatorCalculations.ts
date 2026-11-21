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

function validateValues(values: readonly number[]): void {
  values.forEach((value, index) => {
    if (!Number.isFinite(value)) throw new Error(`Input ${index} is not finite.`);
  });
}

function requireFiniteResult(value: number, label: string): number {
  if (!Number.isFinite(value)) {
    throw new Error(`${label} exceeded the finite numeric range.`);
  }
  return value;
}

function accurateSum(values: readonly number[], scale: number): number {
  // Maintain a non-overlapping floating-point expansion. Plain reduction can
  // lose a small residual between large cancelling values, even after scaling.
  const partials: number[] = [];
  for (let index = 0; index < values.length; index += 1) {
    let value = values[index] / scale;
    let partialIndex = 0;
    for (const partial of partials) {
      let high = value;
      let low = partial;
      if (Math.abs(high) < Math.abs(low)) {
        const swap = high;
        high = low;
        low = swap;
      }
      const sum = high + low;
      const error = low - (sum - high);
      if (error !== 0) partials[partialIndex++] = error;
      value = sum;
    }
    partials.length = partialIndex;
    if (value !== 0) partials.push(value);
  }
  return partials.reduce((sum, partial) => sum + partial, 0);
}

function stableMean(values: readonly number[], knownScale?: number): number {
  let scale = knownScale ?? 0;
  if (knownScale === undefined) {
    for (const value of values) scale = Math.max(scale, Math.abs(value));
  }
  if (scale === 0) return 0;

  let normalizedSum = 0;
  let normalizedMagnitude = 0;
  for (const value of values) {
    const normalized = value / scale;
    normalizedSum += normalized;
    normalizedMagnitude += Math.abs(normalized);
  }
  // Ordinary summation is both faster and accurate enough when cancellation
  // is mild. Use the expansion only when positive/negative terms nearly cancel.
  if (Math.abs(normalizedSum) < normalizedMagnitude * 0.5) {
    normalizedSum = accurateSum(values, scale);
  }
  return requireFiniteResult((normalizedSum / values.length) * scale, 'Indicator mean');
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
  validateValues(values);
  const output: Array<number | null> = Array(values.length).fill(null);
  for (let index = period - 1; index < values.length; index += 1) {
    // Normalize each window before summing. A raw rolling sum can overflow
    // even when the arithmetic mean itself is representable (e.g. MAX + MAX).
    const window = values.slice(index - period + 1, index + 1);
    output[index] = stableMean(window);
  }
  return output;
}

export function calculateEma(values: readonly number[], period: number): Array<number | null> {
  validatePeriod(period);
  validateValues(values);
  const output: Array<number | null> = Array(values.length).fill(null);
  if (values.length < period) return output;
  const seed = values.slice(0, period);
  if (seed.some((value) => !Number.isFinite(value))) {
    throw new Error('EMA input contains a non-finite value.');
  }
  let previous = stableMean(seed);
  output[period - 1] = previous;
  const multiplier = 2 / (period + 1);
  for (let index = period; index < values.length; index += 1) {
    const value = values[index];
    previous = requireFiniteResult(
      previous * (1 - multiplier) + value * multiplier,
      'EMA output',
    );
    output[index] = previous;
  }
  return output;
}

export function calculateRsi(values: readonly number[], period = 14): Array<number | null> {
  validatePeriod(period);
  validateValues(values);
  const output: Array<number | null> = Array(values.length).fill(null);
  if (values.length <= period) return output;

  let averageGain = 0;
  let averageLoss = 0;
  for (let index = 1; index <= period; index += 1) {
    const change = requireFiniteResult(
      values[index] - values[index - 1],
      'RSI price change',
    );
    const gain = Math.max(change, 0);
    const loss = Math.max(-change, 0);
    averageGain += (gain - averageGain) / index;
    averageLoss += (loss - averageLoss) / index;
  }

  const toRsi = () => {
    if (averageLoss === 0) return averageGain === 0 ? 50 : 100;
    const scale = Math.max(averageGain, averageLoss);
    const normalizedGain = averageGain / scale;
    const normalizedLoss = averageLoss / scale;
    return 100 * normalizedGain / (normalizedGain + normalizedLoss);
  };
  output[period] = toRsi();

  for (let index = period + 1; index < values.length; index += 1) {
    const change = requireFiniteResult(
      values[index] - values[index - 1],
      'RSI price change',
    );
    averageGain += (Math.max(change, 0) - averageGain) / period;
    averageLoss += (Math.max(-change, 0) - averageLoss) / period;
    output[index] = requireFiniteResult(toRsi(), 'RSI output');
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
      macdValues.push(requireFiniteResult(fast[index]! - slow[index]!, 'MACD output'));
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
      histogram: signal === null ? null : requireFiniteResult(macd - signal, 'MACD histogram'),
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
  validateValues(values);
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
    const scale = window.reduce((maximum, value) => Math.max(maximum, Math.abs(value)), 0);
    const normalized = scale === 0 ? window.map(() => 0) : window.map((value) => value / scale);
    const mean = stableMean(window, scale);
    const normalizedMean = scale === 0 ? 0 : mean / scale;
    const normalizedVariance = normalized.reduce(
      (sum, value) => sum + ((value - normalizedMean) ** 2),
      0,
    ) / period;
    const deviation = requireFiniteResult(
      Math.sqrt(normalizedVariance) * scale,
      'Bollinger deviation',
    );
    output[index] = {
      middle: mean,
      upper: requireFiniteResult(mean + standardDeviations * deviation, 'Bollinger upper band'),
      lower: requireFiniteResult(mean - standardDeviations * deviation, 'Bollinger lower band'),
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
