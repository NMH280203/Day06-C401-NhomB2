import React from 'react'
import { FoodSuggestion } from '../../lib/types'
import { FoodCard } from './FoodCard'

interface FoodListProps {
  foods: FoodSuggestion[]
}

export function FoodList({ foods }: FoodListProps) {
  if (foods.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-900/40 rounded-2xl border border-slate-800/80">
        <span className="text-4xl mb-2">🍽️</span>
        <h4 className="text-sm font-semibold text-slate-300">Chưa có gợi ý món ăn</h4>
        <p className="text-xs text-slate-500 mt-1 max-w-[200px]">Hãy chat với trợ lý AI để nhận danh sách món ăn ngon!</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {foods.map((food, idx) => (
        <FoodCard key={idx} food={food} />
      ))}
    </div>
  )
}
