import {
  type DeepPartial,
  type ChartOptions,
} from 'lightweight-charts';
import type { Timeframe } from '../types';

export function buildChartOptions(
  timeframe: Timeframe,
  showGrid: boolean,
): DeepPartial<ChartOptions> {
  const gridColor = 'rgba(41, 45, 51, 0.3)';

  return {
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
}
