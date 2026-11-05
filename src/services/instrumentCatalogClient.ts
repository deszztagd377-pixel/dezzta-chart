import type {
  InstrumentCatalogResponse,
  InstrumentRoot,
  FuturesContractDto,
  SupportedInstrumentProduct,
} from '../types/instrumentCatalogApi';

export type InstrumentCatalogErrorCode =
  | 'configuration'
  | 'cancelled'
  | 'timeout'
  | 'network'
  | 'http'
  | 'invalid_json'
  | 'invalid_catalog';

export class InstrumentCatalogError extends Error {
  readonly code: InstrumentCatalogErrorCode;
  readonly statusCode?: number;

  constructor(code: InstrumentCatalogErrorCode, message: string, statusCode?: number) {
    super(message);
    this.name = 'InstrumentCatalogError';
    this.code = code;
    this.statusCode = statusCode;
  }
}

export interface FetchInstrumentCatalogOptions {
  baseUrl: string;
  root?: InstrumentRoot;
  signal?: AbortSignal;
  timeoutMs?: number;
  fetchImpl?: typeof fetch;
}

const ROOTS = ['ES', 'NQ', 'GC'] as const;
const DECIMAL = /^(?:0|[1-9]\d*)(?:\.\d+)?$/;
const UNSIGNED = /^\d+$/;
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isRoot(value: unknown): value is InstrumentRoot {
  return typeof value === 'string' && ROOTS.includes(value as InstrumentRoot);
}

function isValidIsoDate(value: string): boolean {
  if (!ISO_DATE.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00.000Z`);
  return Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}

function parseProduct(value: unknown, index: number): SupportedInstrumentProduct {
  if (!isRecord(value) || !isRoot(value.root) ||
      typeof value.product_name !== 'string' || !value.product_name.trim()) {
    throw new Error(`Invalid supported product at index ${index}.`);
  }
  return { root: value.root, product_name: value.product_name };
}

function parseContract(value: unknown, index: number): FuturesContractDto {
  if (!isRecord(value)) throw new Error(`Contract ${index} must be an object.`);
  if (!isRoot(value.root) ||
      typeof value.product_name !== 'string' ||
      typeof value.dataset !== 'string' || !value.dataset ||
      typeof value.raw_symbol !== 'string' ||
      !Number.isSafeInteger(value.instrument_id) || Number(value.instrument_id) <= 0 ||
      !Number.isSafeInteger(value.publisher_id) || Number(value.publisher_id) <= 0 ||
      value.instrument_class !== 'F' ||
      typeof value.expiration !== 'string' || !isValidIsoDate(value.expiration) ||
      (value.currency !== null && typeof value.currency !== 'string') ||
      (value.min_price_increment !== null &&
        (typeof value.min_price_increment !== 'string' || !DECIMAL.test(value.min_price_increment))) ||
      typeof value.definition_ts_event_ns !== 'string' || !UNSIGNED.test(value.definition_ts_event_ns) ||
      typeof value.provider !== 'string' || !value.provider ||
      value.series_type !== 'contract' ||
      (value.canonical_instrument_id !== null &&
        (typeof value.canonical_instrument_id !== 'string' ||
          !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value.canonical_instrument_id)))) {
    throw new Error(`Contract ${index} has invalid or incomplete provider metadata.`);
  }

  const rawSymbol = value.raw_symbol.toUpperCase();
  const symbolRoot = ROOTS.find((root) => rawSymbol.startsWith(root));
  if (symbolRoot !== value.root || !new RegExp(`^(ES|NQ|GC)[FGHJKMNQUVXZ]\\d{1,2}$`).test(rawSymbol)) {
    throw new Error(`Contract ${index} has a raw symbol inconsistent with its product root.`);
  }

  return {
    root: value.root,
    product_name: value.product_name,
    dataset: value.dataset,
    raw_symbol: rawSymbol,
    instrument_id: Number(value.instrument_id),
    publisher_id: Number(value.publisher_id),
    instrument_class: 'F',
    expiration: value.expiration,
    currency: value.currency as string | null,
    min_price_increment: value.min_price_increment as string | null,
    definition_ts_event_ns: value.definition_ts_event_ns,
    provider: value.provider,
    series_type: 'contract',
    canonical_instrument_id: value.canonical_instrument_id as string | null,
  };
}

/** Runtime validation for the backend catalog response; TypeScript types alone do not validate JSON. */
export function parseInstrumentCatalog(payload: unknown): InstrumentCatalogResponse {
  if (!isRecord(payload) ||
      typeof payload.dataset !== 'string' || !payload.dataset ||
      !['definitions_unavailable', 'ready'].includes(String(payload.state)) ||
      !Array.isArray(payload.supported_products) ||
      !Number.isSafeInteger(payload.contract_count) || Number(payload.contract_count) < 0 ||
      !Array.isArray(payload.contracts) ||
      typeof payload.selection_policy !== 'string' || !payload.selection_policy) {
    throw new Error('Instrument catalog response has an invalid envelope.');
  }

  const products = payload.supported_products.map(parseProduct);
  const contracts = payload.contracts.map(parseContract);
  if (Number(payload.contract_count) !== contracts.length) {
    throw new Error('Instrument catalog contract_count does not match contracts length.');
  }
  // The backend reports global catalog state before applying the optional root
  // filter. A ready global catalog can therefore return zero rows for one root.
  if (payload.state === 'definitions_unavailable' && contracts.length > 0) {
    throw new Error('Instrument catalog state does not match the returned contract list.');
  }
  if (payload.state === 'ready' && contracts.length === 0 && payload.requested_root === undefined) {
    throw new Error('A ready unfiltered catalog cannot contain zero contracts.');
  }

  const productRoots = new Set<InstrumentRoot>();
  for (const product of products) {
    if (productRoots.has(product.root)) throw new Error('Instrument catalog contains duplicate product roots.');
    productRoots.add(product.root);
  }

  const identities = new Set<string>();
  for (const contract of contracts) {
    if (contract.dataset !== payload.dataset || !productRoots.has(contract.root)) {
      throw new Error('Contract dataset or product root does not match the catalog.');
    }
    const identity = [contract.dataset, contract.publisher_id, contract.instrument_id].join('|');
    if (identities.has(identity)) throw new Error('Instrument catalog contains duplicate contract identities.');
    identities.add(identity);
  }

  if (payload.requested_root !== undefined &&
      (!isRoot(payload.requested_root) || contracts.some((item) => item.root !== payload.requested_root))) {
    throw new Error('Instrument catalog contains contracts outside the requested root.');
  }

  return {
    dataset: payload.dataset,
    state: payload.state as InstrumentCatalogResponse['state'],
    supported_products: products,
    contract_count: contracts.length,
    contracts,
    selection_policy: payload.selection_policy,
    ...(payload.requested_root ? { requested_root: payload.requested_root as InstrumentRoot } : {}),
  };
}

function buildCatalogUrl(baseUrl: string, root?: InstrumentRoot): URL {
  if (typeof baseUrl !== 'string' || !baseUrl.trim()) {
    throw new InstrumentCatalogError('configuration', 'Market-data API URL is not configured.');
  }
  let url: URL;
  try {
    const normalized = baseUrl.trim().replace(/\/+$/, '');
    url = new URL('v1/instruments', `${normalized}/`);
  } catch {
    throw new InstrumentCatalogError('configuration', 'Market-data API URL is invalid.');
  }
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) {
    throw new InstrumentCatalogError('configuration', 'Market-data API URL must use HTTP(S) without embedded credentials.');
  }
  if (root) url.searchParams.set('root', root);
  return url;
}

export async function fetchInstrumentCatalog(
  options: FetchInstrumentCatalogOptions,
): Promise<InstrumentCatalogResponse> {
  const timeoutMs = options.timeoutMs ?? 8000;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new InstrumentCatalogError('configuration', 'Catalog timeout must be a positive finite number.');
  }
  if (options.signal?.aborted) {
    throw new InstrumentCatalogError('cancelled', 'Catalog request was cancelled.');
  }

  const url = buildCatalogUrl(options.baseUrl, options.root);
  const requestFetch = options.fetchImpl ?? fetch;
  const controller = new AbortController();
  let timedOut = false;
  const onExternalAbort = () => controller.abort();
  options.signal?.addEventListener('abort', onExternalAbort, { once: true });
  const timeout = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  try {
    const response = await requestFetch(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      cache: 'no-store',
      signal: controller.signal,
    });
    if (!response.ok) {
      throw new InstrumentCatalogError('http', `Instrument catalog returned HTTP ${response.status}.`, response.status);
    }

    let payload: unknown;
    try {
      payload = await response.json();
    } catch {
      throw new InstrumentCatalogError('invalid_json', 'Instrument catalog response is not valid JSON.');
    }

    try {
      return parseInstrumentCatalog(payload);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown catalog validation error.';
      throw new InstrumentCatalogError('invalid_catalog', `Instrument catalog validation failed: ${message}`);
    }
  } catch (error) {
    if (error instanceof InstrumentCatalogError) throw error;
    if (timedOut) throw new InstrumentCatalogError('timeout', `Catalog request exceeded ${timeoutMs} ms.`);
    if (options.signal?.aborted) throw new InstrumentCatalogError('cancelled', 'Catalog request was cancelled.');
    const message = error instanceof Error ? error.message : 'Unknown network error.';
    throw new InstrumentCatalogError('network', `Unable to reach the market-data API: ${message}`);
  } finally {
    clearTimeout(timeout);
    options.signal?.removeEventListener('abort', onExternalAbort);
  }
}
