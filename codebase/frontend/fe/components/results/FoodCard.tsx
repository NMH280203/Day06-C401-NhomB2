import React from 'react'
import { FoodSuggestion } from '../../lib/types'
import { Badge } from '../ui/Badge'

interface FoodCardProps {
  food: FoodSuggestion
}

export function FoodCard({ food }: FoodCardProps) {
  // Format price to VND currency
  const formattedPrice = new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(food.estimated_price)

  return (
    <div className="group relative bg-slate-900/60 backdrop-blur-md border border-slate-800/80 hover:border-orange-500/50 p-5 rounded-2xl transition-all duration-300 shadow-lg hover:shadow-orange-500/5 flex flex-col gap-3">
      <div className="flex justify-between items-start gap-2">
        <h3 className="font-bold text-slate-100 group-hover:text-orange-400 transition-colors text-base">
          {food.name}
        </h3>
        <Badge variant="primary">{food.category}</Badge>
      </div>

      <p className="text-sm text-slate-400 leading-relaxed flex-1">
        {food.description}
      </p>

      {food.reason && (
        <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-850/60">
          <span className="text-xs font-semibold text-orange-400 block mb-1">Gợi ý vì:</span>
          <p className="text-xs text-slate-300 leading-relaxed italic">
            &ldquo;{food.reason}&rdquo;
          </p>
        </div>
      )}

      <div className="flex flex-wrap justify-between items-center gap-2 pt-2 border-t border-slate-800/50">
        <span className="text-sm font-bold text-amber-400">{formattedPrice}</span>
        <div className="flex flex-wrap gap-1">
          {food.tags.map((tag, idx) => (
            <Badge key={idx} variant="secondary" className="text-[10px] px-2 py-0.5">
              #{tag}
            </Badge>
          ))}
        </div>
      </div>
    </div>
  )
}
