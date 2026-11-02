import React, { useEffect, useRef, useState } from 'react';
import {
  createChart,
  CandlestickSeries,
} from 'lightweight-charts';
import type {
  IChartApi,
  DeepPartial,
  ChartOptions,
} from 'lightweight-charts';
import type { Timeframe } from '../types';
import { demoCandles, getDemoCandleValidationErrors } from '../data/demoCandles';

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

    const gridColor = 'rgba(41, 45, 51, 0.3)';
    const chartOptions: DeepPartial<ChartOptions> = {
      layout: {
        background: {
          type: 'solid',
          color: '#0d1117',
        },
        textColor: '#d1d5db',
        fontFamily: 'monospace',
      },
      grid: {
        vertLines: {
          color: gridColor,
          visible: showGrid,
        },
        horzLines: {
          color: gridColor,
          visible: showGrid,
        },
      },
      rightPriceScale: {
        borderColor: '#374151',
      },
      timeScale: {
        borderColor: '#374151',
        barSpacing: 12,
        rightOffset: 5,
        timeVisible: true,
        secondsVisible: timeframe.endsWith('s'),
      },
      crosshair: {
        mode: 0,
        vertLine: {
          color: '#f59e0b',
          width: 1,
          style: 1,
          labelVisible: true,
          labelBackgroundColor: '#f59e0b',
        },
        horzLine: {
          color: '#f59e0b',
          width: 1,
          style: 1,
          labelVisible: true,
          labelBackgroundColor: '#f59e0b',
        },
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
      },
      handleScale: {
        mouseWheel: true,
        pinch: true,
      },
    };

    let chart: IChartApi | null = null;
    let observer: ResizeObserver | null = null;
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

        const { width, height } = container.getBoundingClientRect();
        if (width > 0 && height > 0) {
          activeChart.resize(width, height);
          setIsChartReady(true);
        }
      };

      observer = new ResizeObserver(updateChartSize);
      observer.observe(container);
      updateChartSize();
    } catch (error) {
      console.error('DEZZTA CHART initialization failed:', error);
      if (isActive) {
        setChartError('Chart could not be initialized. Please reload the page.');
      }
      observer?.disconnect();
      chart?.remove();
      chartRef.current = null;
      return;
    }

    return () => {
      isActive = false;
      observer?.disconnect();
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
