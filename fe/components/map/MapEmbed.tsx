"use client";

import type { Restaurant } from "@/lib/types";
import { formatCoords } from "@/lib/geo";

interface MapEmbedProps {
  restaurants: Restaurant[];
  selectedPlaceId?: string | null;
  onSelectPlace?: (placeId: string) => void;
}

function buildFocusEmbedUrl(lat: number, lng: number, pad = 0.004): string {
  return (
    `https://www.openstreetmap.org/export/embed.html` +
    `?bbox=${lng - pad},${lat - pad},${lng + pad},${lat + pad}` +
    `&layer=mapnik&marker=${lat},${lng}`
  );
}

function buildOverviewEmbedUrl(
  items: Array<Restaurant & { lat: number; lng: number }>
): string {
  const lats = items.map((r) => r.lat);
  const lngs = items.map((r) => r.lng);
  const pad = 0.012;
  const first = items[0];
  return (
    `https://www.openstreetmap.org/export/embed.html` +
    `?bbox=${Math.min(...lngs) - pad},${Math.min(...lats) - pad},` +
    `${Math.max(...lngs) + pad},${Math.max(...lats) + pad}` +
    `&layer=mapnik&marker=${first.lat},${first.lng}`
  );
}

export function MapEmbed({
  restaurants,
  selectedPlaceId,
  onSelectPlace,
}: MapEmbedProps) {
  const withCoords = restaurants.filter(
    (r) => r.lat != null && r.lng != null
  ) as Array<Restaurant & { lat: number; lng: number }>;

  const selected =
    withCoords.find((r) => r.place_id === selectedPlaceId) ?? withCoords[0];

  if (restaurants.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-surface-400 text-sm">
        <div className="text-center">
          <span className="text-4xl block mb-2">🗺️</span>
          <p>Chưa có dữ liệu quán ăn để hiển thị bản đồ</p>
        </div>
      </div>
    );
  }

  const selectedCoords = selected ? formatCoords(selected.lat, selected.lng) : null;
  const mapSrc = selected
    ? buildFocusEmbedUrl(selected.lat, selected.lng)
    : withCoords.length > 0
      ? buildOverviewEmbedUrl(withCoords)
      : "";

  return (
    <div className="h-full flex flex-col gap-3">
      {selected && (
        <div className="px-1">
          <p className="text-sm font-medium text-surface-800 truncate">
            📍 {selected.name}
          </p>
          <p className="text-xs text-surface-500 truncate">{selected.address}</p>
          {selectedCoords && (
            <p className="text-[11px] text-surface-400 font-mono mt-0.5">
              🌐 {selectedCoords}
            </p>
          )}
        </div>
      )}

      {mapSrc ? (
        <div className="flex-1 min-h-[280px] rounded-xl overflow-hidden border border-surface-200">
          <iframe
            key={selected?.place_id ?? "overview"}
            className="w-full h-full min-h-[280px]"
            src={mapSrc}
            style={{ border: 0 }}
            loading="lazy"
            title={selected ? `Bản đồ — ${selected.name}` : "OpenStreetMap"}
          />
        </div>
      ) : (
        <div className="flex-1 bg-gradient-to-br from-sky-50 to-emerald-50 rounded-xl border border-surface-200 flex items-center justify-center p-6">
          <p className="text-sm text-surface-500 text-center">
            Bản đồ cần tọa độ quán từ Overpass API
          </p>
        </div>
      )}

      {selected && (
        <a
          href={selected.maps_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-center text-primary-600 hover:text-primary-700 hover:underline"
        >
          Mở {selected.name} trên OpenStreetMap ↗
        </a>
      )}

      <div className="space-y-2 max-h-48 overflow-y-auto">
        {restaurants.map((r) => {
          const isActive = selected?.place_id === r.place_id;
          const hasCoords = r.lat != null && r.lng != null;
          const coordsLabel = formatCoords(r.lat, r.lng);
          return (
            <button
              key={r.place_id}
              type="button"
              disabled={!hasCoords}
              onClick={() => hasCoords && onSelectPlace?.(r.place_id)}
              className={`w-full flex items-center gap-2 p-3 rounded-xl border text-left text-sm transition-all ${
                isActive
                  ? "bg-primary-50 border-primary-400 shadow-sm ring-1 ring-primary-200"
                  : "bg-white border-surface-200 hover:border-primary-300 hover:shadow-md"
              } ${!hasCoords ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
            >
              <span className={isActive ? "text-primary-600" : "text-surface-400"}>
                📍
              </span>
              <div className="flex-1 min-w-0">
                <p
                  className={`font-medium truncate ${
                    isActive ? "text-primary-800" : "text-surface-800"
                  }`}
                >
                  {r.name}
                </p>
                <p className="text-xs text-surface-400 truncate">{r.address}</p>
                {coordsLabel && (
                  <p className="text-[10px] text-surface-400 font-mono truncate">
                    {coordsLabel}
                  </p>
                )}
              </div>
              {isActive && (
                <span className="text-[10px] font-semibold text-primary-600 uppercase">
                  đang xem
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
