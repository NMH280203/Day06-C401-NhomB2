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

  // Cycle through gradient top accents
  const gradients = [
    "from-primary-400/30 to-accent-cyan/20",
    "from-accent-teal/30 to-primary-400/20",
    "from-primary-500/25 to-accent-aqua/15",
    "from-accent-cyan/25 to-accent-teal/15",
  ];

  return (
    <div
      className="group glass-card overflow-hidden animate-slide-up"
      style={{ animationDelay: `${index * 80}ms` }}
    >
      {/* Gradient accent strip */}
      <div
        className={`h-1.5 bg-gradient-to-r ${gradients[index % gradients.length]}`}
      />

      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-2">
          <div>
            <h3 className="font-semibold text-surface-900 group-hover:text-primary-600 transition-colors duration-300">
              {food.name}
            </h3>
            <Badge variant="primary" size="sm" className="mt-1.5">
              {food.category}
            </Badge>
          </div>
          <span className="text-lg font-bold text-primary-600 whitespace-nowrap">
            {formatPrice(food.estimated_price)}
          </span>
        </div>

        {/* Description */}
        <p className="text-sm text-surface-500 mt-2 leading-relaxed">
          {food.description}
        </p>

        {/* Reason */}
        <div className="mt-3 p-3 bg-amber-50/50 rounded-2xl border border-amber-100/50 backdrop-blur-sm">
          <p className="text-xs text-amber-800 flex items-start gap-2">
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
