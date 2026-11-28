import React, { useEffect, useId, useMemo, useRef, useState } from 'react';
import { useAuth } from '../auth/AuthProvider';
import {
  createChart,
  CandlestickSeries,
  LineSeries,
} from 'lightweight-charts';
import type { CandlestickData, IChartApi, LineData } from 'lightweight-charts';
import type { Timeframe } from '../types';
import type { FuturesContractDto } from '../types/instrumentCatalogApi';
import { demoCandles, getDemoCandleValidationErrors } from '../data/demoCandles';
import { ohlcvSeriesSupervisorRegistry } from '../services/ohlcvSeriesSupervisorRegistry';
import { getOhlcvStreamLifecycle } from '../services/ohlcvStreamLifecycle';
import { resetMarketDataSnapshot, isSameMarketSeriesIdentity } from '../services/marketDataStore';
import { marketDataSeriesStore } from '../services/marketDataSeriesStore';
import { useMarketDataSeriesSnapshot } from '../services/useMarketDataSeriesSnapshot';
import { useMarketIndicators } from '../indicators/useMarketIndicators';
import { toCandlestickSeriesData } from '../utils/candlestickSeriesData';
import { buildChartOptions } from '../utils/chartOptions';
import { getMeasurableChartSize } from '../utils/chartViewport';
import { getBucketIdentityForTimeframe } from '../utils/ohlcvBucketPolicy';

interface CandlestickChartProps {
  timeframe: Timeframe;
  showGrid: boolean;
  selectedContract: FuturesContractDto | null;
  marketDataApiBaseUrl: string;
}

type MarketDataStatus = 'demo' | 'loading' | 'ready' | 'degraded' | 'unavailable' | 'error';

const CandlestickChart: React.FC<CandlestickChartProps> = ({
  timeframe,
  showGrid,
  selectedContract,
  marketDataApiBaseUrl,
}) => {
  const { user, getIdToken } = useAuth();
  const panelOwnerId = useId();
  const marketDataIdentity = useMemo(() => {
    if (!selectedContract) return null;
    const bucketIdentity = getBucketIdentityForTimeframe(
      timeframe,
      selectedContract.session_calendar_id,
      selectedContract.session_calendar_version,
    );
    return {
      dataset: selectedContract.dataset,
      publisherId: selectedContract.publisher_id,
      instrumentId: selectedContract.instrument_id,
      rawSymbol: selectedContract.raw_symbol,
      timeframe,
      ...bucketIdentity,
    };
  }, [selectedContract, timeframe]);
  const marketDataSnapshot = useMarketDataSeriesSnapshot(marketDataIdentity);
  const marketIndicators = useMarketIndicators(marketDataIdentity);
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const setSeriesDataRef = useRef<((data: CandlestickData[]) => void) | null>(null);
  const updateSeriesRef = useRef<((data: CandlestickData) => void) | null>(null);
  const setIndicatorDataRef = useRef<((indicators: NonNullable<typeof marketIndicators.indicators> | null, candles: CandlestickData[]) => void) | null>(null);
  const lastRenderedRevisionRef = useRef<number | null>(null);
  const lastRenderedTimestampRef = useRef<number | null>(null);

  const [isChartReady, setIsChartReady] = useState(false);
  const [chartError, setChartError] = useState<string | null>(null);
  const [marketDataStatus, setMarketDataStatus] = useState<MarketDataStatus>('demo');
  const [marketDataDetail, setMarketDataDetail] = useState<string | null>(null);
  const [streamLifecycle, setStreamLifecycle] = useState(() => getOhlcvStreamLifecycle(
    typeof navigator === 'undefined' || navigator.onLine,
    typeof document === 'undefined' ? 'visible' : document.visibilityState,
  ));

  // Mobile browsers may suspend timers while the app is backgrounded.
  // Pause on hidden/pagehide/offline; resume with a fresh authenticated
  // supervisor and snapshot on visible/pageshow/online.
  useEffect(() => {
    const syncLifecycle = () => {
      setStreamLifecycle(getOhlcvStreamLifecycle(
        navigator.onLine,
        document.visibilityState,
      ));
    };
    const pauseForPageHide = () => {
      setStreamLifecycle(getOhlcvStreamLifecycle(navigator.onLine, 'hidden'));
    };

    window.addEventListener('online', syncLifecycle);
    window.addEventListener('offline', syncLifecycle);
    window.addEventListener('pageshow', syncLifecycle);
    window.addEventListener('pagehide', pauseForPageHide);
    document.addEventListener('visibilitychange', syncLifecycle);
    syncLifecycle();

    return () => {
      window.removeEventListener('online', syncLifecycle);
      window.removeEventListener('offline', syncLifecycle);
      window.removeEventListener('pageshow', syncLifecycle);
      window.removeEventListener('pagehide', pauseForPageHide);
      document.removeEventListener('visibilitychange', syncLifecycle);
    };
  }, []);

  useEffect(() => {
    const container = chartContainerRef.current;
    if (!container) return;

    const chartOptions = buildChartOptions(timeframe, showGrid);

    let chart: IChartApi | null = null;
    let observer: ResizeObserver | null = null;
    let removeWindowResizeListener: (() => void) | null = null;
    let isActive = true;

    try {
      const validationErrors = getDemoCandleValidationErrors(demoCandles);
      if (validationErrors.length > 0) {
        throw new Error(`Invalid demo candle fixture: ${validationErrors.join(' ')}`);
      }

      const activeChart = createChart(container, chartOptions);
      chart = activeChart;
      chartRef.current = activeChart;

      const candleSeries = activeChart.addSeries(CandlestickSeries, {
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderDownColor: '#ef5350',
        borderUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        wickUpColor: '#26a69a',
      });

      setSeriesDataRef.current = (data) => candleSeries.setData(data);
      updateSeriesRef.current = (data) => candleSeries.update(data);
      const smaSeries = activeChart.addSeries(LineSeries, {
        color: '#f5c451', lineWidth: 2, priceLineVisible: false,
        lastValueVisible: false, crosshairMarkerVisible: false,
      });
      const emaSeries = activeChart.addSeries(LineSeries, {
        color: '#5da9ff', lineWidth: 2, priceLineVisible: false,
        lastValueVisible: false, crosshairMarkerVisible: false,
      });
      const bollingerMiddleSeries = activeChart.addSeries(LineSeries, {
        color: 'rgba(184, 146, 255, 0.72)', lineWidth: 1, priceLineVisible: false,
        lastValueVisible: false, crosshairMarkerVisible: false,
      });
      const bollingerUpperSeries = activeChart.addSeries(LineSeries, {
        color: 'rgba(184, 146, 255, 0.48)', lineWidth: 1, priceLineVisible: false,
        lastValueVisible: false, crosshairMarkerVisible: false,
      });
      const bollingerLowerSeries = activeChart.addSeries(LineSeries, {
        color: 'rgba(184, 146, 255, 0.48)', lineWidth: 1, priceLineVisible: false,
        lastValueVisible: false, crosshairMarkerVisible: false,
      });
      const toLineData = (values: readonly (number | null)[], candles: CandlestickData[]): LineData[] =>
        values.flatMap((value, index) => (
          value === null || !Number.isFinite(value) || !candles[index]
            ? []
            : [{ time: candles[index].time, value }]
        ));
      setIndicatorDataRef.current = (indicators, candles) => {
        smaSeries.setData(indicators ? toLineData(indicators.sma20, candles) : []);
        emaSeries.setData(indicators ? toLineData(indicators.ema20, candles) : []);
        bollingerMiddleSeries.setData(indicators
          ? toLineData(indicators.bollinger20.map((point) => point.middle), candles) : []);
        bollingerUpperSeries.setData(indicators
          ? toLineData(indicators.bollinger20.map((point) => point.upper), candles) : []);
        bollingerLowerSeries.setData(indicators
          ? toLineData(indicators.bollinger20.map((point) => point.lower), candles) : []);
      };
      lastRenderedRevisionRef.current = null;
      lastRenderedTimestampRef.current = null;
      candleSeries.setData(demoCandles);
      activeChart.timeScale().fitContent();

      const updateChartSize = () => {
        if (!isActive) return;

        const size = getMeasurableChartSize(container.getBoundingClientRect());
        if (size) {
          activeChart.resize(size.width, size.height);
          setIsChartReady(true);
        }
      };

      if (typeof ResizeObserver !== 'undefined') {
        observer = new ResizeObserver(updateChartSize);
        observer.observe(container);
      } else {
        window.addEventListener('resize', updateChartSize, { passive: true });
        removeWindowResizeListener = () => {
          window.removeEventListener('resize', updateChartSize);
        };
      }

      updateChartSize();
    } catch (error) {
      console.error('DEZZTA CHART initialization failed:', error);
      if (isActive) {
        setChartError('Chart could not be initialized. Please reload the page.');
      }
      observer?.disconnect();
      removeWindowResizeListener?.();
      chart?.remove();
      chartRef.current = null;
      setSeriesDataRef.current = null;
      updateSeriesRef.current = null;
      setIndicatorDataRef.current = null;
      lastRenderedRevisionRef.current = null;
      lastRenderedTimestampRef.current = null;
      return;
    }

    return () => {
      isActive = false;
      observer?.disconnect();
      removeWindowResizeListener?.();
      chart?.remove();
      chartRef.current = null;
      setSeriesDataRef.current = null;
      updateSeriesRef.current = null;
      setIndicatorDataRef.current = null;
      lastRenderedRevisionRef.current = null;
      lastRenderedTimestampRef.current = null;
    };
  }, []);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;

    chart.timeScale().applyOptions({
      secondsVisible: timeframe.endsWith('s'),
    });
  }, [timeframe]);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;

    chart.applyOptions({
      grid: {
        vertLines: { visible: showGrid },
        horzLines: { visible: showGrid },
      },
    });
  }, [showGrid]);

  // Each chart reads only its canonical series key. The keyed external store
  // prevents another panel's selection or updates from replacing this snapshot.
  useEffect(() => {
    if (!isChartReady || !selectedContract || !marketDataIdentity) return;

    const snapshot = marketDataSnapshot;
    if (!isSameMarketSeriesIdentity(snapshot.identity, marketDataIdentity)) return;

    if (snapshot.status === 'loading') {
      setSeriesDataRef.current?.(demoCandles);
      lastRenderedRevisionRef.current = null;
      lastRenderedTimestampRef.current = null;
      setMarketDataStatus('loading');
      setMarketDataDetail(snapshot.detail ?? 'Waiting for a fresh validated snapshot.');
      return;
    }

    if (snapshot.status === 'unavailable' || snapshot.status === 'error') {
      setSeriesDataRef.current?.(demoCandles);
      lastRenderedRevisionRef.current = null;
      lastRenderedTimestampRef.current = null;
      setMarketDataStatus(snapshot.status);
      setMarketDataDetail(snapshot.detail ?? 'No verified backend bars are available.');
      return;
    }

    if (snapshot.source !== 'backend' ||
        (snapshot.status !== 'ready' && snapshot.status !== 'degraded')) return;
    const candles = toCandlestickSeriesData(snapshot.bars);
    if (candles.length === 0) return;

    const lastChange = snapshot.lastChange;
    if (
      lastChange.type === 'update' &&
      lastRenderedRevisionRef.current === snapshot.revision - 1 &&
      lastRenderedTimestampRef.current !== null &&
      lastChange.bar.timestamp >= lastRenderedTimestampRef.current &&
      updateSeriesRef.current
    ) {
      const updateCandle = toCandlestickSeriesData([lastChange.bar])[0];
      if (updateCandle) updateSeriesRef.current(updateCandle);
      else setSeriesDataRef.current?.(candles);
    } else {
      // Snapshot replacements, missed revisions, and historical corrections
      // require a full ordered setData. Normal newest-candle updates use the
      // Lightweight Charts incremental API to avoid redrawing the full series.
      setSeriesDataRef.current?.(candles);
    }

    lastRenderedRevisionRef.current = snapshot.revision;
    lastRenderedTimestampRef.current = snapshot.bars[snapshot.bars.length - 1].timestamp;
    setMarketDataStatus(snapshot.status);
    setMarketDataDetail(snapshot.detail ?? `${candles.length} validated bars · ${timeframe}`);
  }, [isChartReady, selectedContract, timeframe, marketDataIdentity, marketDataSnapshot]);

  useEffect(() => {
    if (!isChartReady || !setSeriesDataRef.current) return;

    if (!selectedContract) {
      setSeriesDataRef.current(demoCandles);
      setMarketDataStatus('demo');
      setMarketDataDetail('Offline sample candles. No contract is selected.');
      resetMarketDataSnapshot(null, 'demo', 'Offline sample candles are excluded from indicator calculations.');
      return;
    }

    const identity = marketDataIdentity;
    if (!identity) return;

    const resetSelectedSeries = (
      status: 'loading' | 'unavailable',
      detail: string,
    ) => {
      marketDataSeriesStore.reset(identity, status, detail);
    };

    // A canonical ID must come from the validated instrument catalog. Never
    // derive it from raw_symbol or provider instrument identifiers.
    if (!selectedContract.canonical_instrument_id) {
      setSeriesDataRef.current(demoCandles);
      setMarketDataStatus('unavailable');
      setMarketDataDetail('This contract has no active canonical registry mapping; authenticated streaming is disabled.');
      resetSelectedSeries('unavailable', 'No active canonical instrument mapping exists.');
      return;
    }

    if (!user) {
      setSeriesDataRef.current(demoCandles);
      setMarketDataStatus('unavailable');
      setMarketDataDetail('Sign in with Firebase to request authenticated backend data.');
      resetSelectedSeries('unavailable', 'Firebase sign-in is required.');
      return;
    }

    if (!streamLifecycle.shouldConnect) {
      const detail = streamLifecycle.reason === 'offline'
        ? 'Device is offline. Authenticated market-data streaming is paused until connectivity returns.'
        : 'Chart is in the background. Streaming is paused until the app becomes visible again.';
      setSeriesDataRef.current(demoCandles);
      lastRenderedRevisionRef.current = null;
      lastRenderedTimestampRef.current = null;
      setMarketDataStatus('unavailable');
      setMarketDataDetail(detail);
      resetSelectedSeries('unavailable', detail);
      return;
    }

    // Clear prior series immediately. The supervisor owns the only live
    // transport and obtains an atomic snapshot + watermark before updates.
    setSeriesDataRef.current(demoCandles);
    setMarketDataStatus('loading');
    setMarketDataDetail(`Authenticating WebSocket stream for ${identity.rawSymbol} · ${timeframe}.`);
    resetSelectedSeries('loading', 'Waiting for an authenticated WebSocket snapshot.');

    let releaseLease: (() => void) | null = null;
    try {
      const lease = ohlcvSeriesSupervisorRegistry.acquire({
      baseUrl: marketDataApiBaseUrl,
      identity,
      canonicalInstrumentId: selectedContract.canonical_instrument_id,
      getIdToken,
      onStatus: (status) => {
        if (status === 'connecting' || status === 'reconnecting') {
          setMarketDataStatus('loading');
          setMarketDataDetail(status === 'reconnecting'
            ? 'Stream interrupted; requesting a fresh token and snapshot.'
            : 'Connecting to authenticated market-data WebSocket.');
        } else if (status === 'authenticated') {
          setMarketDataStatus('loading');
          setMarketDataDetail('Firebase identity verified; subscribing to the canonical instrument.');
        } else if (status === 'subscribed') {
          // The validated snapshot replaces demo candles with a different time
          // range; fit once at snapshot arrival, not on every streaming tick.
          chartRef.current?.timeScale().fitContent();
          const snapshot = marketDataSeriesStore.getSnapshot(identity);
          setMarketDataStatus(snapshot.status === 'unavailable'
            ? 'unavailable'
            : snapshot.status === 'degraded' ? 'degraded' : 'ready');
          setMarketDataDetail(snapshot.detail ?? `Authenticated WebSocket · ${identity.rawSymbol} · ${timeframe}`);
        } else if (status === 'stopped') {
          setMarketDataStatus('unavailable');
          setMarketDataDetail('Authenticated market-data stream stopped.');
        }
      },
      onError: (error) => {
        setMarketDataStatus('error');
        setMarketDataDetail(error.message);
      },
      }, panelOwnerId);
      releaseLease = () => lease.release();
    } catch (error) {
      const detail = error instanceof Error ? error.message : 'Unable to acquire the authenticated market-data stream.';
      resetSelectedSeries('unavailable', detail);
      setMarketDataStatus('error');
      setMarketDataDetail(detail);
      return;
    }

    return () => releaseLease?.();
  }, [
    isChartReady,
    marketDataApiBaseUrl,
    selectedContract,
    timeframe,
    user,
    getIdToken,
    streamLifecycle.shouldConnect,
    streamLifecycle.reason,
  ]);

  useEffect(() => {
    if (!isChartReady || !setIndicatorDataRef.current) return;
    const indicators = marketIndicators.source === 'backend' &&
      (marketIndicators.status === 'ready' || marketIndicators.status === 'degraded')
      ? marketIndicators.indicators
      : null;
    const candles = indicators ? toCandlestickSeriesData(marketDataSnapshot.bars) : [];
    setIndicatorDataRef.current(indicators, candles);
  }, [isChartReady, marketDataSnapshot, marketIndicators.indicators, marketIndicators.source, marketIndicators.status]);

  const selectedSymbol = selectedContract?.raw_symbol;
  const badgeText = !selectedSymbol
    ? 'DEMO DATA · SAMPLE OHLC'
    : marketDataStatus === 'loading'
      ? `DEMO · REQUESTING ${selectedSymbol}`
      : marketDataStatus === 'ready'
        ? `BACKEND DATA · ${selectedSymbol} · READY`
        : marketDataStatus === 'degraded'
          ? `BACKEND DATA · ${selectedSymbol} · DEGRADED`
          : marketDataStatus === 'unavailable'
            ? `NO VERIFIED BARS · DEMO (${selectedSymbol})`
            : marketDataStatus === 'error'
              ? `API ERROR · DEMO (${selectedSymbol})`
              : 'DEMO DATA · SAMPLE OHLC';

  const isBackendData = marketDataStatus === 'ready' || marketDataStatus === 'degraded';

  return (
    <div
      ref={chartContainerRef}
      role="region"
      aria-label={selectedSymbol
        ? `Chart for ${selectedSymbol}; data status ${marketDataStatus}`
        : 'Chart area showing sample OHLC data'}
      style={{
        width: '100%',
        height: '100%',
        minHeight: 0,
        position: 'relative',
      }}
    >
      <div
        aria-label={isBackendData ? 'Validated backend OHLCV data' : 'Sample data, not live market data'}
        style={{
          position: 'absolute',
          top: 10,
          left: 10,
          zIndex: 2,
          maxWidth: 'calc(100% - 20px)',
          padding: '6px 8px',
          border: `1px solid ${isBackendData ? '#245c4c' : '#66502b'}`,
          borderRadius: 5,
          background: isBackendData ? 'rgba(14, 37, 31, 0.94)' : 'rgba(25, 22, 17, 0.94)',
          color: isBackendData ? '#8ee0bc' : '#e7bd73',
          fontSize: 9,
          fontWeight: 700,
          letterSpacing: '0.4px',
          pointerEvents: 'none',
          overflowWrap: 'anywhere',
        }}
      >
        {badgeText}
      </div>
      {selectedSymbol && marketDataDetail && (
        <div
          role="status"
          style={{
            position: 'absolute',
            top: 39,
            left: 10,
            zIndex: 2,
            maxWidth: 'min(340px, calc(100% - 20px))',
            padding: '5px 7px',
            borderRadius: 4,
            background: 'rgba(13, 17, 23, 0.88)',
            color: '#aab6c5',
            fontSize: 9,
            lineHeight: 1.45,
            pointerEvents: 'none',
          }}
        >
          {marketDataDetail}
        </div>
      )}
      {chartError ? (
        <div
          role="alert"
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 'calc(100% - 32px)',
            maxWidth: 320,
            color: '#fca5a5',
            fontSize: 13,
            textAlign: 'center',
          }}
        >
          {chartError}
        </div>
      ) : !isChartReady ? (
        <div
          role="status"
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#9ca3af',
            fontSize: 14,
          }}
        >
          Loading chart...
        </div>
      ) : null}
    </div>
  );
};

export default CandlestickChart;
