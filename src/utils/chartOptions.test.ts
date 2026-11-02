import { describe, expect, it } from 'vitest';
import { buildChartOptions } from './chartOptions';

describe('chart interaction options', () => {
  it('keeps mouse drag and wheel scrolling enabled', () => {
    const options = buildChartOptions('1d', true);

    expect(options.handleScroll?.pressedMouseMove).toBe(true);
    expect(options.handleScroll?.mouseWheel).toBe(true);
  });

  it('keeps pinch and wheel scaling enabled', () => {
    const options = buildChartOptions('1d', true);

    expect(options.handleScale?.pinch).toBe(true);
    expect(options.handleScale?.mouseWheel).toBe(true);
  });

  it('applies the grid preference to both grid directions', () => {
    const visible = buildChartOptions('1d', true);
    const hidden = buildChartOptions('1d', false);

    expect(visible.grid?.vertLines?.visible).toBe(true);
    expect(visible.grid?.horzLines?.visible).toBe(true);
    expect(hidden.grid?.vertLines?.visible).toBe(false);
    expect(hidden.grid?.horzLines?.visible).toBe(false);
  });

  it('shows seconds only for second-based intervals', () => {
    expect(buildChartOptions('1s', true).timeScale?.secondsVisible).toBe(true);
    expect(buildChartOptions('1d', true).timeScale?.secondsVisible).toBe(false);
  });
});
