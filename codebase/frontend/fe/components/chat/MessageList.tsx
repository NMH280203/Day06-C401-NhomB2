import React, { useRef, useEffect } from 'react'
import { Message } from '../../lib/types'
import { MessageBubble } from './MessageBubble'
import { Compass, Sparkles } from 'lucide-react'

interface MessageListProps {
  messages: Message[]
  onSendSuggestion: (text: string) => void
}

export function MessageList({ messages, onSendSuggestion }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom on updates
  useEffect(() => {
    // Small timeout to allow images/elements to render
    const timer = setTimeout(() => {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
    return () => clearTimeout(timer)
  }, [messages])

  if (messages.length === 0) {
    const suggestions = [
      { text: '🍜 Phở bò tái lăn gần đây', desc: 'Tìm quán phở ngon trứ danh cách dưới 1km' },
      { text: '🍱 Cơm tấm sườn chả dưới 60k', desc: 'Tìm quán cơm tấm trưa đầy đủ sườn chả giá tốt' },
      { text: '☕ Cà phê trứng Nguyễn Hữu Huân', desc: 'Thèm đồ uống béo ngậy đặc sản Hà Nội' },
      { text: '🥗 Quán cơm chay gần đây', desc: 'Ăn uống lành mạnh, thanh đạm' },
    ]

    return (
      <div className="flex-1 flex flex-col justify-center items-center px-4 py-8 text-center max-w-lg mx-auto">
        <div className="w-16 h-16 rounded-3xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mb-6 shadow-xl shadow-orange-500/5 animate-bounce">
          <Compass className="w-8 h-8 text-orange-400" />
        </div>
        <h2 className="text-xl font-extrabold text-slate-100 mb-2 flex items-center gap-2">
          <span>Khám Phá Ẩm Thực AI</span>
          <Sparkles className="w-4 h-4 text-orange-400 fill-orange-400/20" />
        </h2>
        <p className="text-sm text-slate-400 mb-8 leading-relaxed">
          Chào bạn! Hãy chia sẻ khẩu vị, ngân sách hoặc vị trí hiện tại, tôi sẽ gợi ý món ăn & nhà hàng lý tưởng nhất cho bạn.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => onSendSuggestion(s.text)}
              className="text-left p-3.5 rounded-2xl bg-slate-900/40 hover:bg-slate-900/70 border border-slate-800/80 hover:border-orange-500/30 transition-all duration-300 active:scale-95 group"
            >
              <div className="text-xs font-bold text-slate-200 group-hover:text-orange-400 transition-colors">
                {s.text}
              </div>
              <div className="text-[10px] text-slate-500 mt-1">
                {s.desc}
              </div>
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 custom-scrollbar">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} onSendSuggestion={onSendSuggestion} />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
