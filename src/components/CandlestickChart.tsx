import React, { useEffect, useRef, useState } from 'react';
import { useAuth } from '../auth/AuthProvider';
import {
  createChart,
  CandlestickSeries,
} from 'lightweight-charts';
import type { CandlestickData, IChartApi } from 'lightweight-charts';
import type { Timeframe } from '../types';
import type { FuturesContractDto } from '../types/instrumentCatalogApi';
import { demoCandles, getDemoCandleValidationErrors } from '../data/demoCandles';
import { startOhlcvStreamSupervisor } from '../services/ohlcvStreamSupervisor';
import {
  getMarketDataSnapshot,
  publishMarketDataSnapshot,
  resetMarketDataSnapshot,
  subscribeMarketData,
} from '../services/marketDataStore';
import { toCandlestickSeriesData } from '../utils/candlestickSeriesData';
import { buildChartOptions } from '../utils/chartOptions';
import { getMeasurableChartSize } from '../utils/chartViewport';

interface CandlestickChartProps {
  timeframe: Timeframe;
  showGrid: boolean;
  selectedContract: FuturesContractDto | null;
  marketDataApiBaseUrl: string;
}

type MarketDataStatus = 'demo' | 'loading' | 'ready' | 'degraded' | 'unavailable' | 'error';

interface SeriesIdentity {
  dataset: string;
  publisherId: number;
  instrumentId: number;
  rawSymbol: string;
}

const CandlestickChart: React.FC<CandlestickChartProps> = ({
  timeframe,
  showGrid,
  selectedContract,
  marketDataApiBaseUrl,
}) => {
  const { user, getIdToken } = useAuth();
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const setSeriesDataRef = useRef<((data: CandlestickData[]) => void) | null>(null);

  const [isChartReady, setIsChartReady] = useState(false);
  const [chartError, setChartError] = useState<string | null>(null);
  const [marketDataStatus, setMarketDataStatus] = useState<MarketDataStatus>('demo');
  const [marketDataDetail, setMarketDataDetail] = useState<string | null>(null);

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
      return;
    }

    return () => {
      isActive = false;
      observer?.disconnect();
      removeWindowResizeListener?.();
      chart?.remove();
      chartRef.current = null;
      setSeriesDataRef.current = null;
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

  // The shared store is the single update path for both HTTP snapshots and
  // authenticated WebSocket revisions. This keeps the chart current without
  // coupling chart rendering to the transport implementation.
  useEffect(() => {
    if (!isChartReady || !selectedContract) return;

    const syncFromStore = () => {
      const snapshot = getMarketDataSnapshot();
      const identity = snapshot.identity;
      if (
        !identity ||
        identity.dataset !== selectedContract.dataset ||
        identity.publisherId !== selectedContract.publisher_id ||
        identity.instrumentId !== selectedContract.instrument_id ||
        identity.rawSymbol !== selectedContract.raw_symbol ||
        identity.timeframe !== timeframe
      ) {
        return;
      }

      if (snapshot.status === 'loading') {
        setSeriesDataRef.current?.(demoCandles);
        setMarketDataStatus('loading');
        setMarketDataDetail(snapshot.detail ?? 'Waiting for a fresh validated snapshot.');
        return;
      }

      if (snapshot.status === 'unavailable' || snapshot.status === 'error') {
        setSeriesDataRef.current?.(demoCandles);
        setMarketDataStatus(snapshot.status);
        setMarketDataDetail(snapshot.detail ?? 'No verified backend bars are available.');
        return;
      }

      if (snapshot.source !== 'backend' ||
          (snapshot.status !== 'ready' && snapshot.status !== 'degraded')) return;
      const candles = toCandlestickSeriesData(snapshot.bars);
      if (candles.length === 0) return;
      setSeriesDataRef.current?.(candles);
      setMarketDataStatus(snapshot.status);
      setMarketDataDetail(snapshot.detail ?? `${candles.length} validated bars · ${timeframe}`);
    };

    const unsubscribe = subscribeMarketData(syncFromStore);
    syncFromStore();
    return unsubscribe;
  }, [isChartReady, selectedContract, timeframe]);

  useEffect(() => {
    if (!isChartReady || !setSeriesDataRef.current) return;

    if (!selectedContract) {
      setSeriesDataRef.current(demoCandles);
      setMarketDataStatus('demo');
      setMarketDataDetail('Offline sample candles. No contract is selected.');
      resetMarketDataSnapshot(null, 'demo', 'Offline sample candles are excluded from indicator calculations.');
      return;
    }

    const identity = {
      dataset: selectedContract.dataset,
      publisherId: selectedContract.publisher_id,
      instrumentId: selectedContract.instrument_id,
      rawSymbol: selectedContract.raw_symbol,
      timeframe,
    };

    // A canonical ID must come from the validated instrument catalog. Never
    // derive it from raw_symbol or provider instrument identifiers.
    if (!selectedContract.canonical_instrument_id) {
      setSeriesDataRef.current(demoCandles);
      setMarketDataStatus('unavailable');
      setMarketDataDetail('This contract has no active canonical registry mapping; authenticated streaming is disabled.');
      resetMarketDataSnapshot(identity, 'unavailable', 'No active canonical instrument mapping exists.');
      return;
    }

    if (!user) {
      setSeriesDataRef.current(demoCandles);
      setMarketDataStatus('unavailable');
      setMarketDataDetail('Sign in with Firebase to request authenticated backend data.');
      resetMarketDataSnapshot(identity, 'unavailable', 'Firebase sign-in is required.');
      return;
    }

    // Clear prior series immediately. The supervisor owns the only live
    // transport and obtains an atomic snapshot + watermark before updates.
    setSeriesDataRef.current(demoCandles);
    setMarketDataStatus('loading');
    setMarketDataDetail(`Authenticating WebSocket stream for ${identity.rawSymbol} · ${timeframe}.`);
    resetMarketDataSnapshot(identity, 'loading', 'Waiting for an authenticated WebSocket snapshot.');

    const supervisor = startOhlcvStreamSupervisor({
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
          const snapshot = getMarketDataSnapshot();
          setMarketDataStatus(snapshot.status === 'degraded' ? 'degraded' : 'ready');
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
    });

    return () => supervisor.stop();
  }, [
    isChartReady,
    marketDataApiBaseUrl,
    selectedContract,
    timeframe,
    user,
    getIdToken,
  ]);

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
