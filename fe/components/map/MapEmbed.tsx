import type { Restaurant } from "@/lib/types";

interface MapEmbedProps {
  restaurants: Restaurant[];
}

export function MapEmbed({ restaurants }: MapEmbedProps) {
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY || "";

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

  // Build markers string for Google Maps Embed API
  // Using the first restaurant as center
  const center = restaurants[0];
  const markersParam = restaurants
    .map((r) => `${encodeURIComponent(r.address)}`)
    .join("|");

  // Use Place mode for single, or Search mode for multiple
  const mapSrc =
    restaurants.length === 1
      ? `https://www.google.com/maps/embed/v1/place?key=${apiKey}&q=${encodeURIComponent(center.address)}&zoom=15`
      : `https://www.google.com/maps/embed/v1/search?key=${apiKey}&q=${encodeURIComponent(markersParam)}&zoom=13`;

  // Fallback if no API key
  if (!apiKey || apiKey === "YOUR_KEY") {
    return (
      <div className="h-full flex flex-col">
        <div className="flex-1 bg-gradient-to-br from-sky-50 to-emerald-50 rounded-xl border border-surface-200 overflow-hidden flex flex-col items-center justify-center p-6">
          <span className="text-5xl mb-3">🗺️</span>
          <p className="text-sm text-surface-600 text-center mb-4">
            Cần Google Maps API Key để hiển thị bản đồ
          </p>
          <div className="space-y-2 w-full max-w-sm">
            {restaurants.map((r) => (
              <a
                key={r.place_id}
                href={r.maps_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 p-3 bg-white rounded-xl border border-surface-200 hover:border-primary-300 hover:shadow-md transition-all text-sm group"
              >
                <span className="text-primary-500 group-hover:scale-110 transition-transform">
                  📍
                </span>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-surface-800 truncate">
                    {r.name}
                  </p>
                  <p className="text-xs text-surface-400 truncate">
                    {r.address}
                  </p>
                </div>
                <svg
                  className="w-4 h-4 text-surface-400 group-hover:text-primary-500 transition-colors"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"
                  />
                </svg>
              </a>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full rounded-xl overflow-hidden border border-surface-200">
      <iframe
        className="w-full h-full min-h-[400px]"
        src={mapSrc}
        style={{ border: 0 }}
        allowFullScreen
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        title="Restaurant locations"
      />
    </div>
  );
}
