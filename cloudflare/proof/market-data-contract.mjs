const GENERATION_ID = "synthetic-v1";
const DIGEST_DOMAIN = "dezzta-ohlcv-event-v1";
const ALLOWED_TIMEFRAMES = new Set(["1m", "5m", "15m", "1h"]);
const ID_PATTERN = /^[A-Za-z0-9._:-]{1,128}$/;

const INTERVAL_NS = {
  "1m": 60_000_000_000n,
  "5m": 300_000_000_000n,
  "15m": 900_000_000_000n,
  "1h": 3_600_000_000_000n,
};

function isPositiveInteger(value) {
  return Number.isSafeInteger(value) && value > 0;
}

export function validateSyntheticCanonicalSeries(series) {
  if (!series || typeof series !== "object" || Array.isArray(series)) return false;
  return typeof series.seriesKey === "string" &&
    series.seriesKey.length <= 128 && ID_PATTERN.test(series.seriesKey) &&
    series.provider === "synthetic" &&
    series.seriesType === "contract" &&
    typeof series.dataset === "string" && /^[A-Z0-9._-]{1,24}$/.test(series.dataset) &&
    isPositiveInteger(series.publisherId) &&
    isPositiveInteger(series.instrumentId) &&
    typeof series.rawSymbol === "string" && /^[A-Z0-9._-]{1,24}$/.test(series.rawSymbol) &&
    ALLOWED_TIMEFRAMES.has(series.timeframe) &&
    (series.bucketPolicy === undefined || series.bucketPolicy === "UTC_LEGACY") &&
    (series.calendarId === undefined || series.calendarId === "") &&
    (series.calendarVersion === undefined || series.calendarVersion === "");
}

function hashSeed(value) {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function cents(value) {
  return (value / 100).toFixed(2);
}

function sha256Hex(value) {
  return crypto.subtle.digest("SHA-256", new TextEncoder().encode(value))
    .then((digest) => Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join(""));
}

export function createSyntheticCanonicalBar(series, sequence, receivedAtNs) {
  if (!validateSyntheticCanonicalSeries(series)) throw new TypeError("Invalid synthetic canonical series.");
  if (!isPositiveInteger(sequence) || sequence > 1_000_000_000) throw new RangeError("Invalid synthetic event sequence.");
  if (typeof receivedAtNs !== "string" || !/^\d{1,32}$/.test(receivedAtNs)) {
    throw new TypeError("Invalid synthetic receive timestamp.");
  }
  const seed = hashSeed(series.seriesKey);
  const openCents = 9_500_000 + ((seed + sequence * 37) % 80_000);
  const closeCents = 9_500_000 + ((seed * 7 + sequence * 53) % 80_000);
  const highCents = Math.max(openCents, closeCents) + 50 + (sequence % 70);
  const lowCents = Math.max(1, Math.min(openCents, closeCents) - 40 - (sequence % 60));
  const startNs = (1_700_000_000_000_000_000n + BigInt(sequence) * INTERVAL_NS[series.timeframe]).toString();
  return {
    dataset: series.dataset,
    publisherId: series.publisherId,
    instrumentId: series.instrumentId,
    rawSymbol: series.rawSymbol,
    timeframe: series.timeframe,
    bucketPolicy: series.bucketPolicy ?? "UTC_LEGACY",
    calendarId: "",
    calendarVersion: "",
    tsStartNs: startNs,
    open: cents(openCents),
    high: cents(highCents),
    low: cents(lowCents),
    close: cents(closeCents),
    volume: String(100 + ((seed + sequence * 13) % 5_000)),
    tsEventNs: startNs,
    tsReceivedNs: receivedAtNs,
    sequence,
    sequenceOrigin: "local",
    provider: "synthetic",
    seriesType: "contract",
    origin: "derived",
    completeness: "complete",
  };
}

function canonicalEventDigestInput({ series, generationId, cursor, emittedAtNs, operation, isFinal, bar }) {
  return JSON.stringify([
    DIGEST_DOMAIN,
    [series.seriesKey, series.provider, series.seriesType, series.dataset, series.publisherId,
      series.instrumentId, series.rawSymbol, series.timeframe, series.bucketPolicy ?? "",
      series.calendarId ?? "", series.calendarVersion ?? ""],
    generationId,
    cursor,
    emittedAtNs,
    operation,
    isFinal,
    [bar.dataset, bar.publisherId, bar.instrumentId, bar.rawSymbol, bar.timeframe,
      bar.bucketPolicy ?? "", bar.calendarId ?? "", bar.calendarVersion ?? "",
      bar.tsStartNs, bar.open, bar.high, bar.low, bar.close, bar.volume, bar.tsEventNs,
      bar.tsReceivedNs, bar.sequence, bar.sequenceOrigin ?? "", bar.provider ?? "",
      bar.seriesType ?? "", bar.origin ?? "", bar.completeness ?? ""],
  ]);
}

export async function createSyntheticUpdateEnvelope(series, sequence, emittedAtNs) {
  if (!validateSyntheticCanonicalSeries(series)) throw new TypeError("Invalid synthetic canonical series.");
  if (typeof emittedAtNs !== "string" || !/^\d{1,32}$/.test(emittedAtNs)) throw new TypeError("Invalid emittedAtNs.");
  const bar = createSyntheticCanonicalBar(series, sequence, emittedAtNs);
  const event = {
    type: "market_data.ohlcv.update",
    version: 1,
    streamId: "synthetic:" + series.seriesKey,
    eventId: series.seriesKey + ":" + GENERATION_ID + ":" + sequence,
    cursor: String(sequence),
    sequence,
    emittedAtNs,
    operation: "upsert",
    isFinal: true,
    series,
    bar,
    generationId: GENERATION_ID,
    provenance: {
      mode: "synthetic",
      dataStatus: "synthetic_only",
      provider: null,
      dataset: series.dataset,
      asOfNs: emittedAtNs,
      providerConnected: false,
    },
  };
  event.digest = await sha256Hex(canonicalEventDigestInput(event));
  return event;
}

export async function createSyntheticSnapshotEnvelope(series, bars, highWaterCursor) {
  if (!validateSyntheticCanonicalSeries(series)) throw new TypeError("Invalid synthetic canonical series.");
  if (!Array.isArray(bars) || bars.length < 1 || bars.length > 5000) throw new RangeError("Invalid snapshot bar count.");
  if (!Number.isSafeInteger(highWaterCursor) || highWaterCursor < 1) throw new RangeError("Invalid snapshot high-water cursor.");
  const asOfNs = bars[bars.length - 1].tsReceivedNs;
  const snapshot = {
    type: "market_data.ohlcv.snapshot",
    version: 1,
    state: "ready",
    timestampUnit: "nanoseconds",
    priceRepresentation: "decimal-string",
    bars,
    detail: null,
    count: bars.length,
    truncated: false,
    generationId: GENERATION_ID,
    highWaterCursor: String(highWaterCursor),
    retentionFloorCursor: String(bars[0].sequence),
    provenance: {
      mode: "synthetic",
      dataStatus: "synthetic_only",
      provider: null,
      dataset: series.dataset,
      asOfNs,
      providerConnected: false,
    },
  };
  snapshot.snapshotDigest = await sha256Hex(JSON.stringify([
    "dezzta-ohlcv-snapshot-v1",
    [series.seriesKey, series.provider, series.seriesType, series.dataset,
      series.publisherId, series.instrumentId, series.rawSymbol, series.timeframe,
      series.bucketPolicy ?? "", series.calendarId ?? "", series.calendarVersion ?? ""],
    snapshot.generationId,
    snapshot.highWaterCursor,
    snapshot.retentionFloorCursor,
    snapshot.bars,
  ]));
  return snapshot;
}

export function createProtocolError(code, retryable, correlationId, message) {
  const allowed = new Set([
    "invalid_request", "invalid_series", "unsupported_version", "unauthorized",
    "forbidden", "ticket_expired", "ticket_replayed", "generation_mismatch",
    "cursor_invalid", "cursor_expired", "replay_limit_exceeded", "digest_mismatch",
    "ack_regression", "rate_limited", "temporarily_unavailable", "internal_error",
  ]);
  if (!allowed.has(code) || typeof retryable !== "boolean" ||
      typeof correlationId !== "string" || !ID_PATTERN.test(correlationId) ||
      typeof message !== "string" || message.length < 1 || message.length > 256) {
    throw new TypeError("Invalid market-data protocol error envelope.");
  }
  return { type: "market_data.error", version: 1, code, retryable, correlationId, message };
}
