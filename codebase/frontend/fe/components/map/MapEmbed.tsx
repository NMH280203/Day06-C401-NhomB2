import React from 'react'
import { Restaurant } from '../../lib/types'
import { useChatStore } from '../../hooks/useChatStore'

interface MapEmbedProps {
  restaurants: Restaurant[]
}

export function MapEmbed({ restaurants }: MapEmbedProps) {
  const userLocation = useChatStore((state) => state.context.location)
  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY

  // Default coordinate (Hanoi centre)
  const defaultLat = 21.0285
  const defaultLng = 105.8542

  // For the iframe, we try to use coordinate of first restaurant or fallback to user location
  // Note: we can parse lat/lng from restaurant or user location if available
  // Let's assume some coordinates for mock restaurants if not present,
  // Pho Thin: 21.0175, 105.8559
  // Bun Cha Huong Lien: 21.0189, 105.8532
  // Giang Cafe: 21.0348, 105.8543
  // Coffee House: 21.0227, 105.8519
  // Kieu Giang: 10.7937, 106.7214
  // Com Ga Hai Nam: 10.7997, 106.6908
  
  const getCoordinates = (r: Restaurant) => {
    if (r.place_id === 'res_5') return { lat: 21.0175, lng: 105.8559 } // Pho Thin
    if (r.place_id === 'res_6') return { lat: 21.0189, lng: 105.8532 } // Bun Cha Huong Lien
    if (r.place_id === 'res_1') return { lat: 21.0348, lng: 105.8543 } // Giang
    if (r.place_id === 'res_2') return { lat: 21.0227, lng: 105.8519 } // Coffee House
    if (r.place_id === 'res_3') return { lat: 10.7937, lng: 106.7214 } // Kieu Giang
    if (r.place_id === 'res_4') return { lat: 10.7997, lng: 106.6908 } // Com Ga
    return { lat: defaultLat, lng: defaultLng }
  }

  const activeRes = restaurants[0]
  const coords = activeRes ? getCoordinates(activeRes) : (userLocation || { lat: defaultLat, lng: defaultLng })
  const lat = coords.lat
  const lng = coords.lng

  // If Google Maps key is set
  if (apiKey && apiKey !== 'YOUR_KEY' && apiKey.trim() !== '') {
    let query = 'restaurants'
    if (restaurants.length > 0) {
      query = restaurants.map((r) => r.name).join(' OR ')
    } else if (userLocation?.address) {
      query = userLocation.address
    }
    const embedUrl = `https://www.google.com/maps/embed/v1/search?key=${apiKey}&q=${encodeURIComponent(query)}&zoom=15`

    return (
      <div className="w-full h-full min-h-[350px] rounded-2xl overflow-hidden border border-slate-700/50 shadow-xl bg-slate-900">
        <iframe
          width="100%"
          height="100%"
          style={{ border: 0 }}
          loading="lazy"
          allowFullScreen
          referrerPolicy="no-referrer-when-downgrade"
          src={embedUrl}
        />
      </div>
    )
  }

  // Fallback: OpenStreetMap Embed with a gorgeous dark overlay filter
  const delta = 0.008
  const bbox = `${lng - delta}%2C${lat - delta}%2C${lng + delta}%2C${lat + delta}`
  const osmUrl = `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${lat}%2C${lng}`

  return (
    <div className="relative w-full h-full min-h-[350px] rounded-2xl overflow-hidden border border-slate-700/50 shadow-xl bg-slate-950 flex flex-col">
      <div className="flex-1 relative min-h-[300px]">
        <iframe
          width="100%"
          height="100%"
          style={{ border: 0, filter: 'invert(90%) hue-rotate(180deg) brightness(0.95)' }}
          loading="lazy"
          src={osmUrl}
        />
      </div>
      <div className="bg-slate-900/90 border-t border-slate-800/80 p-3 text-xs text-slate-300 backdrop-blur-md">
        <div className="font-semibold text-orange-400 mb-1 flex items-center gap-1.5">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
          </span>
          Bản đồ gợi ý ({restaurants.length} địa điểm)
        </div>
        <div className="truncate text-slate-400">
          {activeRes ? `Đang hiển thị khu vực xung quanh ${activeRes.name}` : 'Hiển thị khu vực hiện tại của bạn'}
        </div>
      </div>
    </div>
  )
}
