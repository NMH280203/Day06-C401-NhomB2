'use client'

import React, { useState, useEffect } from 'react'
import { ChatWindow } from '../../components/chat/ChatWindow'
import { ResultPanel } from '../../components/results/ResultPanel'
import { useGeolocation } from '../../hooks/useGeolocation'
import { useChat } from '../../hooks/useChat'
import { Button } from '../../components/ui/Button'
import { MapPin, Trash2, Compass, AlertCircle } from 'lucide-react'

export default function ChatPage() {
  const [mounted, setMounted] = useState(false)
  const { location, request, loading: geoLoading, error: geoError } = useGeolocation()
  const { clearHistory, messages } = useChat()

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-screen bg-slate-950">
        <div className="w-10 h-10 border-4 border-orange-500 border-t-transparent animate-spin rounded-full" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full relative">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 bg-slate-950/60 border-b border-slate-900 backdrop-blur-md z-30 flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-orange-500 to-amber-500 flex items-center justify-center shadow-md shadow-orange-500/10">
            <span className="text-base">🍔</span>
          </div>
          <span className="font-extrabold text-slate-100 tracking-tight bg-gradient-to-r from-orange-400 to-amber-300 bg-clip-text text-transparent">
            FoodieAI
          </span>
        </div>

        {/* Location Info & Clear Button */}
        <div className="flex items-center gap-2">
          {location ? (
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-555 bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 max-w-xs">
              <MapPin className="w-3.5 h-3.5 flex-shrink-0 animate-bounce" />
              <span className="truncate">{location.address}</span>
            </div>
          ) : (
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-800 border border-slate-705 border-slate-700 text-xs text-slate-400">
              <MapPin className="w-3.5 h-3.5 flex-shrink-0" />
              <span>Vị trí chưa xác định</span>
            </div>
          )}

          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearHistory}
              className="text-xs gap-1.5 border border-slate-800 text-slate-400 hover:text-slate-205 hover:text-slate-200 hover:border-slate-700"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Xóa lịch sử</span>
            </Button>
          )}
        </div>
      </header>

      {/* Geolocation Banner */}
      {!location && (
        <div className="bg-orange-500/10 border-b border-orange-500/20 px-4 py-3 flex flex-col sm:flex-row items-center justify-between gap-3 backdrop-blur-sm z-20 flex-shrink-0">
          <div className="flex items-center gap-2.5 text-xs sm:text-sm text-slate-200">
            <Compass className="w-4 h-4 text-orange-400 flex-shrink-0 animate-spin" style={{ animationDuration: '6s' }} />
            <span>
              Cho phép truy cập vị trí để tìm quán ăn & đặc sản ngon gần bạn nhất.
            </span>
            {geoError && (
              <span className="text-red-400 text-xs flex items-center gap-1 ml-2">
                <AlertCircle className="w-3 h-3" /> {geoError}
              </span>
            )}
          </div>
          <Button
            variant="primary"
            size="sm"
            onClick={request}
            isLoading={geoLoading}
            className="text-xs px-3.5 py-1.5 font-bold shadow-md w-full sm:w-auto"
          >
            Cho phép
          </Button>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-row overflow-hidden relative">
        <main className="flex-1 h-full overflow-hidden flex flex-col">
          <ChatWindow />
        </main>
        <ResultPanel />
      </div>
    </div>
  )
}
