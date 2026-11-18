import { describe, expect, it } from 'vitest';
import { getOhlcvStreamLifecycle } from './ohlcvStreamLifecycle';

describe('OHLCV stream browser lifecycle', () => {
  it('connects only while online and visible', () => {
    expect(getOhlcvStreamLifecycle(true, 'visible')).toEqual({
      online: true,
      visible: true,
      shouldConnect: true,
      reason: 'active',
    });
  });

  it('pauses while offline even if the document is visible', () => {
    expect(getOhlcvStreamLifecycle(false, 'visible')).toEqual({
      online: false,
      visible: true,
      shouldConnect: false,
      reason: 'offline',
    });
  });

  it('pauses while hidden even if the browser reports online', () => {
    expect(getOhlcvStreamLifecycle(true, 'hidden')).toEqual({
      online: true,
      visible: false,
      shouldConnect: false,
      reason: 'hidden',
    });
  });

  it('prioritizes offline state when both lifecycle constraints apply', () => {
    expect(getOhlcvStreamLifecycle(false, 'hidden')).toEqual({
      online: false,
      visible: false,
      shouldConnect: false,
      reason: 'offline',
    });
  });

  it('treats prerender and other non-visible states as hidden', () => {
    expect(getOhlcvStreamLifecycle(true, 'prerender').shouldConnect).toBe(false);
  });
});
