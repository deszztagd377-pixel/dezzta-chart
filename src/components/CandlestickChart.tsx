import React, { useEffect, useRef, useState } from 'react';
import {
createChart,
CandlestickSeries,
} from 'lightweight-charts';
import type {
IChartApi,
ISeriesApi,
CandlestickData,
DeepPartial,
ChartOptions,
} from 'lightweight-charts';
import type { Timeframe } from '../types';

interface CandlestickChartProps {
timeframe: Timeframe;
}

// Sample OHLC data — not live market data
const sampleCandles: CandlestickData[] = [
{ time: '2024-01-01', open: 100.0, high: 105.5, low: 98.2, close: 103.8 },
{ time: '2024-01-02', open: 103.8, high: 107.2, low: 102.1, close: 106.5 },
{ time: '2024-01-03', open: 106.5, high: 108.0, low: 104.3, close: 105.2 },
{ time: '2024-01-04', open: 105.2, high: 109.8, low: 104.5, close: 108.7 },
{ time: '2024-01-05', open: 108.7, high: 110.5, low: 107.3, close: 109.1 },
{ time: '2024-01-08', open: 109.1, high: 112.4, low: 108.6, close: 111.8 },
{ time: '2024-01-09', open: 111.8, high: 113.2, low: 110.5, close: 112.3 },
{ time: '2024-01-10', open: 112.3, high: 114.0, low: 111.2, close: 113.5 },
{ time: '2024-01-11', open: 113.5, high: 115.8, low: 112.7, close: 114.9 },
{ time: '2024-01-12', open: 114.9, high: 116.2, low: 113.8, close: 115.4 },
{ time: '2024-01-15', open: 115.4, high: 117.5, low: 114.8, close: 116.9 },
{ time: '2024-01-16', open: 116.9, high: 118.3, low: 116.1, close: 117.7 },
{ time: '2024-01-17', open: 117.7, high: 119.0, low: 116.5, close: 118.2 },
{ time: '2024-01-18', open: 118.2, high: 120.5, low: 117.8, close: 119.8 },
{ time: '2024-01-19', open: 119.8, high: 121.2, low: 119.1, close: 120.7 },
{ time: '2024-01-22', open: 120.7, high: 122.8, low: 120.3, close: 122.1 },
{ time: '2024-01-23', open: 122.1, high: 123.5, low: 121.4, close: 122.8 },
{ time: '2024-01-24', open: 122.8, high: 124.2, low: 122.0, close: 123.7 },
{ time: '2024-01-25', open: 123.7, high: 125.0, low: 123.2, close: 124.5 },
{ time: '2024-01-26', open: 124.5, high: 126.3, low: 124.1, close: 125.8 },
];

const CandlestickChart: React.FC<CandlestickChartProps> = ({
timeframe,
}) => {
const chartContainerRef = useRef<HTMLDivElement>(null);
const chartRef = useRef<IChartApi | null>(null);
const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

const [containerSize, setContainerSize] = useState({
width: 0,
height: 0,
});

// Create chart once
useEffect(() => {
const container = chartContainerRef.current;
if (!container) return;

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
      color: 'rgba(41, 45, 51, 0.3)',  
    },  
    horzLines: {  
      color: 'rgba(41, 45, 51, 0.3)',  
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

const chart = createChart(container, chartOptions);  
chartRef.current = chart;  

const candleSeries = chart.addSeries(CandlestickSeries, {  
  upColor: '#26a69a',  
  downColor: '#ef5350',  
  borderDownColor: '#ef5350',  
  borderUpColor: '#26a69a',  
  wickDownColor: '#ef5350',  
  wickUpColor: '#26a69a',  
});  

candleSeriesRef.current = candleSeries;  
candleSeries.setData(sampleCandles);  

chart.timeScale().fitContent();  

const updateChartSize = () => {  
  const { width, height } = container.getBoundingClientRect();  

  setContainerSize({ width, height });  

  if (width > 0 && height > 0) {  
    chart.resize(width, height);  
  }  
};  

const observer = new ResizeObserver(updateChartSize);  
observer.observe(container);  

updateChartSize();  

return () => {  
  observer.disconnect();  
  chart.remove();  
  chartRef.current = null;  
  candleSeriesRef.current = null;  
};

}, []);

// Update time scale display when timeframe changes
useEffect(() => {
const chart = chartRef.current;
if (!chart) return;

chart.timeScale().applyOptions({  
  secondsVisible: timeframe.endsWith('s'),  
});

}, [timeframe]);

return (
<div
ref={chartContainerRef}
style={{
width: '100%',
height: '100%',
minHeight: '400px',
position: 'relative',
}}
>
{containerSize.width === 0 && (
<div
style={{
position: 'absolute',
top: '50%',
left: '50%',
transform: 'translate(-50%, -50%)',
color: '#9ca3af',
fontSize: '14px',
}}
>
Loading chart...
</div>
)}
</div>
);
};

export default CandlestickChart;
