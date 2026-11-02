import React, { useEffect, useRef, useState } from 'react';
import {
  createChart,
  CandlestickSeries,
} from 'lightweight-charts';
import type { IChartApi } from 'lightweight-charts';
import type { Timeframe } from '../types';
import { demoCandles, getDemoCandleValidationErrors } from '../data/demoCandles';
import { buildChartOptions } from '../utils/chartOptions';
import { getMeasurableChartSize } from '../utils/chartViewport';

interface CandlestickChartProps {
  timeframe: Timeframe;
  showGrid: boolean;
}

const CandlestickChart: React.FC<CandlestickChartProps> = ({
  timeframe,
  showGrid,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  const [isChartReady, setIsChartReady] = useState(false);
  const [chartError, setChartError] = useState<string | null>(null);

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
        // Older webviews can still resize the chart through the window event.
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
      return;
    }

    return () => {
      isActive = false;
      observer?.disconnect();
      removeWindowResizeListener?.();
      chart?.remove();
      chartRef.current = null;
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

  return (
    <div
      ref={chartContainerRef}
      role="region"
      aria-label="Chart area showing sample OHLC data"
      style={{
        width: '100%',
        height: '100%',
        minHeight: 0,
        position: 'relative',
      }}
    >
      <div
        aria-label="Sample data, not live market data"
        style={{
          position: 'absolute',
          top: 10,
          left: 10,
          zIndex: 2,
          padding: '5px 8px',
          border: '1px solid #66502b',
          borderRadius: 5,
          background: 'rgba(25, 22, 17, 0.92)',
          color: '#e7bd73',
          fontSize: 9,
          fontWeight: 700,
          letterSpacing: '0.6px',
          pointerEvents: 'none',
        }}
      >
        DEMO DATA · SAMPLE OHLC
      </div>
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
