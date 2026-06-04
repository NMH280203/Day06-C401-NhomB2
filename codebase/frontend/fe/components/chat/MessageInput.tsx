import React, { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

interface MessageInputProps {
  onSendMessage: (text: string) => void
  isLoading: boolean
}

export function MessageInput({ onSendMessage, isLoading }: MessageInputProps) {
  const [text, setText] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-expand logic (up to 4 lines)
  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    // Reset height
    textarea.style.height = 'auto'
    
    // Calculate new height (limit to ~4 lines, approx 110px)
    const newHeight = Math.min(textarea.scrollHeight, 110)
    textarea.style.height = `${newHeight}px`
  }, [text])

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!text.trim() || isLoading) return
    onSendMessage(text.trim())
    setText('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-end gap-2 p-3 bg-slate-900/50 border border-slate-800/80 rounded-2xl focus-within:border-orange-500/40 transition-colors backdrop-blur-md"
    >
      <textarea
        ref={textareaRef}
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={isLoading ? 'Đang chờ trợ lý phản hồi...' : 'Thèm ăn gì, hỏi AI ngay...'}
        disabled={isLoading}
        className="flex-1 bg-transparent border-0 outline-none focus:ring-0 text-sm text-slate-105 text-slate-100 placeholder-slate-500 resize-none max-h-[110px] min-h-[24px] py-1 px-1 custom-scrollbar disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={!text.trim() || isLoading}
        className="flex items-center justify-center w-9 h-9 rounded-xl bg-orange-500 text-white hover:bg-orange-600 disabled:opacity-30 disabled:hover:bg-orange-500 transition-all duration-300 disabled:cursor-not-allowed flex-shrink-0"
      >
        <Send className="w-4 h-4" />
      </button>
    </form>
  )
}
