export interface ChartContainerSize {
  width: number;
  height: number;
}

/**
 * Returns a measurable chart size, or null while the container is hidden,
 * collapsed, or reports invalid dimensions.
 */
export function getMeasurableChartSize(
  rect: Pick<DOMRectReadOnly, 'width' | 'height'>,
): ChartContainerSize | null {
  const { width, height } = rect;

  if (
    !Number.isFinite(width) ||
    !Number.isFinite(height) ||
    width <= 0 ||
    height <= 0
  ) {
    return null;
  }

  return { width, height };
}
