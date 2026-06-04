/** Định dạng tọa độ GPS hiển thị trên UI. */
export function formatCoords(
  lat?: number | null,
  lng?: number | null,
  precision = 6
): string | null {
  if (lat == null || lng == null) return null;
  return `${lat.toFixed(precision)}, ${lng.toFixed(precision)}`;
}
