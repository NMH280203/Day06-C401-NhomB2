import type { Restaurant } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";

interface RestaurantCardProps {
  restaurant: Restaurant;
  index: number;
}

export function RestaurantCard({ restaurant, index }: RestaurantCardProps) {
  const priceLabel = "₫".repeat(restaurant.price_level);

  const renderStars = (rating: number) => {
    const full = Math.floor(rating);
    const hasHalf = rating - full >= 0.3;
    const stars: string[] = [];
    for (let i = 0; i < full; i++) stars.push("★");
    if (hasHalf) stars.push("☆");
    return stars.join("");
  };

  return (
    <div
      className="group glass-card overflow-hidden animate-slide-up"
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <div className="p-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-surface-900 group-hover:text-primary-600 transition-colors duration-300 truncate">
              {restaurant.name}
            </h3>
            <p className="text-xs text-surface-400 mt-1 truncate">
              📍 {restaurant.address}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
            <Badge
              variant={restaurant.is_open ? "success" : "error"}
              size="sm"
            >
              {restaurant.is_open ? "Đang mở" : "Đã đóng"}
            </Badge>
            <span className="text-xs text-surface-400 font-medium">
              {restaurant.distance_km.toFixed(1)} km
            </span>
          </div>
        </div>

        {/* Rating & Price */}
        <div className="flex items-center gap-3 mt-3">
          <div className="flex items-center gap-1">
            <span className="text-amber-400 text-sm">{renderStars(restaurant.rating)}</span>
            <span className="text-xs font-semibold text-surface-700">
              {restaurant.rating}
            </span>
          </div>
          <span className="text-surface-300">•</span>
          <span className="text-sm font-medium text-primary-600">
            {priceLabel}
          </span>
          {restaurant.score > 0 && (
            <>
              <span className="text-surface-300">•</span>
              <span className="text-xs text-surface-400">
                Score: {restaurant.score}
              </span>
            </>
          )}
        </div>

        {/* Featured dishes */}
        {restaurant.featured_dishes.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {restaurant.featured_dishes.map((dish) => (
              <Badge key={dish} variant="default" size="sm">
                {dish}
              </Badge>
            ))}
          </div>
        )}

        {/* Phone & Map */}
        <div className="flex items-center gap-2 mt-3.5 pt-3.5 border-t border-white/30">
          {restaurant.phone && (
            <a
              href={`tel:${restaurant.phone}`}
              className="flex items-center gap-1.5 text-xs text-surface-400 hover:text-primary-600 transition-colors duration-300"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 002.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 01-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 00-1.091-.852H4.5A2.25 2.25 0 002.25 4.5v2.25z" />
              </svg>
              {restaurant.phone}
            </a>
          )}
          <div className="flex-1" />
          <a
            href={restaurant.maps_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-primary-600 hover:text-primary-700 bg-primary-50/50 px-3 py-1.5 rounded-xl hover:bg-primary-100/50 transition-all duration-300 hover:shadow-glow-sm backdrop-blur-sm"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
            </svg>
            Xem bản đồ
          </a>
        </div>
      </div>
    </div>
  );
}
