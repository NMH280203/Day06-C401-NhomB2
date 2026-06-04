import React from 'react'
import { Message } from '../../lib/types'
import { TypingIndicator } from './TypingIndicator'
import { FoodList } from '../results/FoodList'
import { RestaurantList } from '../results/RestaurantList'

interface MessageBubbleProps {
  message: Message
  onSendSuggestion: (suggestion: string) => void
}

export function MessageBubble({ message, onSendSuggestion }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  // If status is present (i.e. thinking status), render TypingIndicator instead of content
  if (message.status) {
    return (
      <div className="flex justify-start mb-4">
        <TypingIndicator statusText={message.status} />
      </div>
    )
  }

  // Format timestamp
  const timeString = new Date(message.timestamp).toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
  })

  // Format content as paragraph (handling double newlines and simple bold tags)
  const formatText = (text: string) => {
    return text.split('\n\n').map((paragraph, index) => {
      const parts = paragraph.split(/(\*\*.*?\*\*)/g)
      return (
        <p key={index} className={index > 0 ? 'mt-2 text-sm' : 'text-sm'}>
          {parts.map((part, i) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return (
                <strong key={i} className="font-semibold text-white">
                  {part.slice(2, -2)}
                </strong>
              )
            }
            return part
          })}
        </p>
      )
    })
  }

  return (
    <div className={`flex flex-col mb-6 ${isUser ? 'items-end' : 'items-start'}`}>
      {/* Bubble Container */}
      <div
        className={`relative max-w-[85%] rounded-2xl px-4 py-3 border shadow-md transition-all ${
          isUser
            ? 'bg-gradient-to-br from-orange-500 to-amber-600 border-orange-500/20 text-white rounded-tr-none'
            : 'bg-slate-900/60 border-slate-800/80 text-slate-200 rounded-tl-none'
        }`}
      >
        {/* Content */}
        <div className="leading-relaxed break-words">
          {message.content ? formatText(message.content) : <span className="text-slate-500 italic">...</span>}
        </div>

        {/* Time Stamp */}
        <span className="block text-[9px] text-slate-500 mt-1.5 text-right font-light">
          {timeString}
        </span>
      </div>

      {/* Embedded Food List */}
      {message.foods && message.foods.length > 0 && (
        <div className="mt-3 w-full max-w-[85%]">
          <div className="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1.5 px-1">
            <span>🍽️</span> Gợi ý món ăn:
          </div>
          <FoodList foods={message.foods} />
        </div>
      )}

      {/* Embedded Restaurant List */}
      {message.restaurants && message.restaurants.length > 0 && (
        <div className="mt-3 w-full max-w-[85%]">
          <div className="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1.5 px-1">
            <span>🏪</span> Quán ăn gợi ý:
          </div>
          <RestaurantList restaurants={message.restaurants} />
        </div>
      )}

      {/* Follow Up Suggestion Chips */}
      {message.follow_up_suggestions && message.follow_up_suggestions.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3 max-w-[85%]">
          {message.follow_up_suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => onSendSuggestion(suggestion)}
              className="text-xs text-orange-400 bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/20 px-3 py-1.5 rounded-full transition-all duration-300 active:scale-95 text-left"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
