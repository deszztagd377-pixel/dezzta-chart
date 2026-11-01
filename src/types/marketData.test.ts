import { describe, expect, it } from 'vitest';
import { databentoPriceToDecimalString } from './marketData';

describe('databentoPriceToDecimalString', () => {
  it('converts positive fixed-point integers exactly', () => {
    expect(databentoPriceToDecimalString('250000000')).toBe('0.25');
    expect(databentoPriceToDecimalString('1234567890123456789')).toBe('1234567890.123456789');
  });

  it('converts negative fixed-point integers exactly', () => {
    expect(databentoPriceToDecimalString('-1250000000')).toBe('-1.25');
  });

  it('removes trailing fractional zeroes', () => {
    expect(databentoPriceToDecimalString('1200000000')).toBe('1.2');
  });

  it('rejects non-integer strings', () => {
    expect(() => databentoPriceToDecimalString('12.5')).toThrow();
    expect(() => databentoPriceToDecimalString('abc')).toThrow();
    expect(() => databentoPriceToDecimalString('')).toThrow();
  });
});
