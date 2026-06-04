import type { Restaurant } from "@/lib/types";
import { RestaurantCard } from "./RestaurantCard";

interface RestaurantListProps {
  restaurants: Restaurant[];
  onViewOnMap?: (restaurant: Restaurant) => void;
}

export function RestaurantList({ restaurants, onViewOnMap }: RestaurantListProps) {
  if (restaurants.length === 0) return null;

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-surface-400 uppercase tracking-wider flex items-center gap-2">
        <span>🏪</span>
        <span>Quán ăn gần bạn</span>
        <span className="bg-accent-teal/10 text-emerald-700 text-xs px-2.5 py-0.5 rounded-full font-bold backdrop-blur-sm">
          {restaurants.length}
        </span>
      </h3>
      <div className="grid gap-3">
        {restaurants.map((restaurant, i) => (
          <RestaurantCard
            key={restaurant.place_id}
            restaurant={restaurant}
            index={i}
            onViewOnMap={onViewOnMap}
          />
        ))}
      </div>
    </div>
  );
}
