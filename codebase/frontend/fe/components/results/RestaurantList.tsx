import React from 'react'
import { Restaurant } from '../../lib/types'
import { RestaurantCard } from './RestaurantCard'

interface RestaurantListProps {
  restaurants: Restaurant[]
}

export function RestaurantList({ restaurants }: RestaurantListProps) {
  if (restaurants.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-900/40 rounded-2xl border border-slate-800/80">
        <span className="text-4xl mb-2">🏪</span>
        <h4 className="text-sm font-semibold text-slate-300">Chưa có quán ăn gợi ý</h4>
        <p className="text-xs text-slate-500 mt-1 max-w-[200px]">Hãy hỏi trợ lý AI để tìm các địa điểm ăn uống ngon gần bạn!</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {restaurants.map((res) => (
        <RestaurantCard key={res.place_id} restaurant={res} />
      ))}
    </div>
  )
}
