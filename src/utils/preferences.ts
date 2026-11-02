export type StorageAccessor = () => Pick<Storage, 'getItem' | 'setItem'>;

export const SHOW_GRID_STORAGE_KEY = 'dezzta-chart:show-grid';

export function readBooleanPreference(
  getStorage: StorageAccessor,
  key: string,
  fallback: boolean,
): boolean {
  try {
    const storedValue = getStorage().getItem(key);
    if (storedValue === null) return fallback;
    if (storedValue === 'true') return true;
    if (storedValue === 'false') return false;
    return fallback;
  } catch {
    return fallback;
  }
}

export function writeBooleanPreference(
  getStorage: StorageAccessor,
  key: string,
  value: boolean,
): void {
  try {
    getStorage().setItem(key, String(value));
  } catch {
    // Preferences remain usable for the current session when storage is unavailable.
  }
}
