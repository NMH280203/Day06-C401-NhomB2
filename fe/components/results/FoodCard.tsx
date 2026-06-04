import type { FoodSuggestion } from "@/lib/types";
import { Badge } from "@/components/ui/Badge";

interface FoodCardProps {
  food: FoodSuggestion;
  index: number;
}

export function FoodCard({ food, index }: FoodCardProps) {
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
    }).format(price);
  };

  // Cycle through gradient backgrounds
  const gradients = [
    "from-primary-500/10 to-amber-500/10",
    "from-emerald-500/10 to-sky-500/10",
    "from-violet-500/10 to-rose-500/10",
    "from-sky-500/10 to-primary-500/10",
  ];

  return (
    <div
      className="group relative bg-white rounded-2xl border border-surface-200 overflow-hidden hover:shadow-xl hover:shadow-surface-900/5 transition-all duration-300 hover:-translate-y-0.5 animate-slide-up"
      style={{ animationDelay: `${index * 80}ms` }}
    >
      {/* Gradient header */}
      <div
        className={`h-2 bg-gradient-to-r ${gradients[index % gradients.length]}`}
      />

      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-2">
          <div>
            <h3 className="font-semibold text-surface-900 group-hover:text-primary-600 transition-colors">
              {food.name}
            </h3>
            <Badge variant="primary" size="sm" className="mt-1">
              {food.category}
            </Badge>
          </div>
          <span className="text-lg font-bold text-primary-600 whitespace-nowrap">
            {formatPrice(food.estimated_price)}
          </span>
        </div>

        {/* Description */}
        <p className="text-sm text-surface-600 mt-2 leading-relaxed">
          {food.description}
        </p>

        {/* Reason */}
        <div className="mt-3 p-2.5 bg-amber-50 rounded-xl border border-amber-100">
          <p className="text-xs text-amber-800 flex items-start gap-1.5">
            <span className="text-amber-500 mt-0.5 flex-shrink-0">💡</span>
            <span>{food.reason}</span>
          </p>
        </div>

        {/* Tags */}
        {food.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {food.tags.map((tag) => (
              <Badge key={tag} variant="default" size="sm">
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
