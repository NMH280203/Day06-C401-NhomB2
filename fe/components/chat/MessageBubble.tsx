"use client";

import type { Message } from "@/lib/types";
import { FoodList } from "@/components/results/FoodList";
import { RestaurantList } from "@/components/results/RestaurantList";
import { TypingIndicator } from "./TypingIndicator";

interface MessageBubbleProps {
  message: Message;
  index?: number;
  isLast?: boolean;
  isLoading?: boolean;
  onSuggestionClick?: (text: string) => void;
}

export function MessageBubble({
  message,
  index = 0,
  isLast = false,
  isLoading = false,
  onSuggestionClick,
}: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isStreaming =
    isLoading &&
    isLast &&
    message.role === "assistant" &&
    !!message.content &&
    !message.follow_up_suggestions?.length;

  const enterAnim = isUser ? "animate-slide-in-right" : "animate-slide-in-left";
  const delay = Math.min(index * 35, 210);

  if (message.role === "assistant" && message.status && !message.content) {
    return (
      <div
        className="flex justify-start opacity-0 animate-slide-in-left"
        style={{ animationDelay: `${delay}ms` }}
      >
        <TypingIndicator text={message.status} />
      </div>
    );
  }

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} opacity-0 ${enterAnim}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div
        className={`max-w-[85%] sm:max-w-[75%] ${isUser ? "order-2" : "order-1"}`}
      >
        <div
          className={`flex items-end gap-2.5 ${isUser ? "flex-row-reverse" : "flex-row"}`}
        >
          <div
            className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center text-sm transition-transform duration-300 hover:scale-110 ${
              isUser
                ? "bg-gradient-to-br from-primary-400 to-primary-600 text-white shadow-glow-sm"
                : "glass border border-white/30 text-surface-600"
            }`}
          >
            {isUser ? "👤" : "🤖"}
          </div>

          <div
            className={`rounded-2xl px-4 py-3 transition-all duration-300 ${
              isUser
                ? "btn-glow text-white rounded-br-lg"
                : `glass-card !rounded-bl-lg text-surface-800 ${
                    isStreaming ? "animate-stream-glow" : ""
                  }`
            }`}
          >
            {message.content && (
              <div
                className={`text-sm leading-relaxed whitespace-pre-wrap ${
                  isUser ? "text-white" : "text-surface-800"
                }`}
              >
                {renderContent(message.content)}
                {isStreaming && (
                  <span className="inline-block w-0.5 h-4 ml-0.5 bg-primary-500 align-middle animate-pulse" />
                )}
              </div>
            )}
          </div>
        </div>

        {!isUser && (message.foods?.length || message.restaurants?.length) ? (
          <div className="ml-10 mt-3 space-y-3 animate-tab-fade">
            {message.foods && message.foods.length > 0 && (
              <FoodList foods={message.foods} />
            )}
            {message.restaurants && message.restaurants.length > 0 && (
              <RestaurantList restaurants={message.restaurants} />
            )}
          </div>
        ) : null}

        {!isUser &&
          message.follow_up_suggestions &&
          message.follow_up_suggestions.length > 0 && (
            <div className="ml-10 mt-3 flex flex-wrap gap-2 stagger-children">
              {message.follow_up_suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => onSuggestionClick?.(suggestion)}
                  className="text-xs px-3.5 py-1.5 rounded-full glass-card !rounded-full text-primary-700 font-medium hover:!bg-primary-50/80 hover:text-primary-600 hover:scale-105 transition-all duration-300 hover:shadow-glow-sm active:scale-95"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}

        <p
          className={`text-[10px] text-surface-400 mt-2 opacity-0 animate-fade-in ${
            isUser ? "text-right mr-10" : "ml-10"
          }`}
          style={{ animationDelay: `${delay + 120}ms` }}
        >
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  );
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderContent(text: string): React.ReactNode {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return <span key={i}>{part}</span>;
  });
}
