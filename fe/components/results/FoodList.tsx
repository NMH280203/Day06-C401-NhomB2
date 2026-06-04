import type { FoodSuggestion } from "@/lib/types";
import { FoodCard } from "./FoodCard";

interface FoodListProps {
  foods: FoodSuggestion[];
}

export function FoodList({ foods }: FoodListProps) {
  if (foods.length === 0) return null;

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-surface-400 uppercase tracking-wider flex items-center gap-2">
        <span>🍜</span>
        <span>Món ăn gợi ý</span>
        <span className="bg-primary-100/50 text-primary-700 text-xs px-2.5 py-0.5 rounded-full font-bold backdrop-blur-sm">
          {foods.length}
        </span>
      </h3>
      <div className="grid gap-3">
        {foods.map((food, i) => (
          <FoodCard key={`${food.name}-${i}`} food={food} index={i} />
        ))}
      </div>
    </div>
  );
}
