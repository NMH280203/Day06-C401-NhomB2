import React from 'react'

interface TypingIndicatorProps {
  statusText?: string
}

export function TypingIndicator({ statusText = 'Trợ lý đang suy nghĩ...' }: TypingIndicatorProps) {
  return (
    <div className="flex items-center gap-3 p-4 bg-slate-900/40 border border-slate-800/80 rounded-2xl w-fit max-w-[85%] animate-pulse">
      <div className="flex gap-1.5">
        <span className="w-2 h-2 rounded-full bg-orange-455 bg-orange-400 animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 rounded-full bg-orange-455 bg-orange-400 animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 rounded-full bg-orange-455 bg-orange-400 animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-xs font-medium text-slate-400">{statusText}</span>
    </div>
  )
}
