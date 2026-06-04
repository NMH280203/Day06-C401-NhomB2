import React from 'react'
import { Restaurant } from '../../lib/types'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { Star, MapPin, Phone, ExternalLink } from 'lucide-react'

interface RestaurantCardProps {
  restaurant: Restaurant
}

export function RestaurantCard({ restaurant }: RestaurantCardProps) {
  // Format rating stars
  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-0.5 text-amber-400">
        <Star className="w-3.5 h-3.5 fill-current" />
        <span className="text-xs font-bold ml-1 text-slate-200">{rating}</span>
      </div>
    )
  }

  // Format price level as dollar signs
  const renderPriceLevel = (level: number) => {
    return (
      <span className="text-xs font-semibold text-emerald-400">
        {'$'.repeat(level)}
      </span>
    )
  }

  return (
    <div className="group relative bg-slate-900/60 backdrop-blur-md border border-slate-800/80 hover:border-orange-500/50 p-5 rounded-2xl transition-all duration-300 shadow-lg hover:shadow-orange-500/5 flex flex-col gap-3">
      {restaurant.photo_url && (
        <div className="w-full h-32 rounded-xl overflow-hidden mb-2 relative">
          <img
            src={restaurant.photo_url}
            alt={restaurant.name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute top-2 right-2">
            <Badge variant={restaurant.is_open ? 'success' : 'glass'}>
              {restaurant.is_open ? 'Đang mở cửa' : 'Đóng cửa'}
            </Badge>
          </div>
        </div>
      )}

      <div className="flex justify-between items-start gap-2">
        <div>
          <h3 className="font-bold text-slate-100 group-hover:text-orange-400 transition-colors text-base">
            {restaurant.name}
          </h3>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            {renderStars(restaurant.rating)}
            <span className="text-slate-600 text-xs">•</span>
            {renderPriceLevel(restaurant.price_level)}
            <span className="text-slate-600 text-xs">•</span>
            <span className="text-xs text-slate-400">{restaurant.distance_km} km</span>
          </div>
        </div>
        {!restaurant.photo_url && (
          <Badge variant={restaurant.is_open ? 'success' : 'secondary'}>
            {restaurant.is_open ? 'Mở cửa' : 'Đóng cửa'}
          </Badge>
        )}
      </div>

      <div className="flex flex-col gap-1.5 text-xs text-slate-400 mt-1">
        <div className="flex items-start gap-1.5">
          <MapPin className="w-3.5 h-3.5 mt-0.5 text-slate-500 flex-shrink-0" />
          <span className="line-clamp-2">{restaurant.address}</span>
        </div>
        {restaurant.phone && (
          <div className="flex items-center gap-1.5">
            <Phone className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
            <span>{restaurant.phone}</span>
          </div>
        )}
      </div>

      {restaurant.featured_dishes && restaurant.featured_dishes.length > 0 && (
        <div className="mt-1">
          <span className="text-[10px] font-bold text-slate-550 uppercase tracking-wider block mb-1">Món ăn nổi tiếng:</span>
          <div className="flex flex-wrap gap-1">
            {restaurant.featured_dishes.map((dish, idx) => (
              <Badge key={idx} variant="glass" className="text-[10px] bg-slate-800/40 text-slate-350">
                {dish}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {restaurant.score && (
        <div className="flex items-center justify-between text-xs pt-2 mt-1 border-t border-slate-800/50">
          <span className="text-slate-500">Điểm số:</span>
          <span className="font-bold text-orange-400 bg-orange-400/10 px-2 py-0.5 rounded-md border border-orange-500/20">{restaurant.score}/10</span>
        </div>
      )}

      <div className="pt-2">
        <a
          href={restaurant.maps_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block w-full"
        >
          <Button variant="secondary" size="sm" className="w-full text-xs gap-1.5 py-2">
            <span>Xem bản đồ</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Button>
        </a>
      </div>
    </div>
  )
}
