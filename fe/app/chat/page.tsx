"use client";

import { ChatWindow } from "@/components/chat/ChatWindow";
import { ResultPanel } from "@/components/results/ResultPanel";
import { AnimatedBackground } from "@/components/ui/AnimatedBackground";
import { useGeolocation } from "@/hooks/useGeolocation";
import { useChatStore } from "@/store/chatStore";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export default function ChatPage() {
  const { location, loading: geoLoading, request: requestLocation } = useGeolocation();
  const context = useChatStore((s) => s.context);
  const results = useChatStore((s) => s.results);
  const clearHistory = useChatStore((s) => s.clearHistory);

  const hasLocation = !!context.location || !!location;

  return (
    <div className="h-screen flex flex-col relative">
      <AnimatedBackground />
      <header className="flex-shrink-0 glass-navbar z-30 animate-slide-down">
        <div className="flex items-center justify-between px-5 sm:px-8 py-4">
          {/* Left: App brand */}
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary-400 via-primary-500 to-primary-600 flex items-center justify-center shadow-glow animate-glow-pulse">
              <span className="text-lg">🍜</span>
            </div>
            <div>
              <h1 className="text-base font-bold text-gradient-cyan">
                FoodChat AI
              </h1>
              <p className="text-[10px] text-surface-400 font-medium tracking-wide -mt-0.5">
                Gợi ý món ăn thông minh
              </p>
            </div>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-3">
            {/* Location badge */}
            {hasLocation && (
              <Badge variant="success" size="sm" className="hidden sm:inline-flex">
                <span className="mr-1">📍</span>
                {context.location
                  ? `${context.location.lat.toFixed(3)}, ${context.location.lng.toFixed(3)}`
                  : "Đã xác định"}
              </Badge>
            )}

            {/* Clear history */}
            <Button
              variant="ghost"
              size="sm"
              onClick={clearHistory}
              className="text-surface-400 hover:text-red-400"
              aria-label="Xóa lịch sử"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
                />
              </svg>
            </Button>
          </div>
        </div>

        {/* Location banner */}
        {!hasLocation && (
          <div className="px-5 sm:px-8 pb-4 animate-slide-down">
            <div className="flex items-center gap-3 p-3.5 glass-card hover:shadow-glow-sm transition-shadow duration-300">
              <span className="text-xl">📍</span>
              <p className="flex-1 text-sm text-surface-600">
                Cho phép truy cập vị trí để tìm quán gần bạn
              </p>
              <Button
                size="sm"
                onClick={requestLocation}
                isLoading={geoLoading}
              >
                Cho phép
              </Button>
            </div>
          </div>
        )}
      </header>

      {/* ─── Main Content ───────────────────────────────────────── */}
      <main className="flex-1 flex overflow-hidden">
        {/* Chat */}
        <div className="flex-1 flex flex-col min-w-0">
          <ChatWindow />
        </div>

        {/* Result panel (desktop) */}
        <ResultPanel
          foods={results.foods}
          restaurants={results.restaurants}
        />
      </main>
    </div>
  );
}
