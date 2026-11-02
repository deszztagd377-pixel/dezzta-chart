import { describe, expect, it } from 'vitest';
import {
  readBooleanPreference,
  writeBooleanPreference,
  SHOW_GRID_STORAGE_KEY,
} from './preferences';

function createMemoryStorage() {
  const values = new Map<string, string>();

  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => values.set(key, value),
  };
}

describe('chart boolean preferences', () => {
  it('uses the fallback when no saved preference exists', () => {
    const storage = createMemoryStorage();
    expect(readBooleanPreference(() => storage, SHOW_GRID_STORAGE_KEY, true)).toBe(true);
  });

  it('reads a saved true preference', () => {
    const storage = createMemoryStorage();
    storage.setItem(SHOW_GRID_STORAGE_KEY, 'true');
    expect(readBooleanPreference(() => storage, SHOW_GRID_STORAGE_KEY, false)).toBe(true);
  });

  it('reads a saved false preference', () => {
    const storage = createMemoryStorage();
    storage.setItem(SHOW_GRID_STORAGE_KEY, 'false');
    expect(readBooleanPreference(() => storage, SHOW_GRID_STORAGE_KEY, true)).toBe(false);
  });

  it('uses the fallback for malformed stored values', () => {
    const storage = createMemoryStorage();
    storage.setItem(SHOW_GRID_STORAGE_KEY, 'yes');
    expect(readBooleanPreference(() => storage, SHOW_GRID_STORAGE_KEY, true)).toBe(true);
  });

  it('falls back safely when storage access throws', () => {
    const getStorage = () => {
      throw new Error('Storage blocked');
    };
    expect(readBooleanPreference(getStorage, SHOW_GRID_STORAGE_KEY, true)).toBe(true);
  });

  it('writes the current preference value', () => {
    const storage = createMemoryStorage();
    writeBooleanPreference(() => storage, SHOW_GRID_STORAGE_KEY, false);
    expect(storage.getItem(SHOW_GRID_STORAGE_KEY)).toBe('false');
  });

  it('does not throw when writing is unavailable', () => {
    const getStorage = () => {
      throw new Error('Storage blocked');
    };
    expect(() => writeBooleanPreference(getStorage, SHOW_GRID_STORAGE_KEY, true)).not.toThrow();
  });
});
