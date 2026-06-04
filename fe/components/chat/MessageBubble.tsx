"use client";

import type { Message } from "@/lib/types";
import { FoodList } from "@/components/results/FoodList";
import { RestaurantList } from "@/components/results/RestaurantList";
import { TypingIndicator } from "./TypingIndicator";

interface MessageBubbleProps {
  message: Message;
  onSuggestionClick?: (text: string) => void;
}

export function MessageBubble({
  message,
  onSuggestionClick,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  // Show typing indicator if message has a status (thinking state)
  if (message.role === "assistant" && message.status && !message.content) {
    return (
      <div className="flex justify-start animate-fade-in">
        <TypingIndicator text={message.status} />
      </div>
    );
  }

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in`}
    >
      <div
        className={`max-w-[85%] sm:max-w-[75%] ${isUser ? "order-2" : "order-1"}`}
      >
        {/* Avatar */}
        <div
          className={`flex items-end gap-2 ${isUser ? "flex-row-reverse" : "flex-row"}`}
        >
          <div
            className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm ${
              isUser
                ? "bg-gradient-to-br from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/20"
                : "bg-gradient-to-br from-surface-100 to-surface-200 text-surface-600"
            }`}
          >
            {isUser ? "👤" : "🤖"}
          </div>

          {/* Bubble */}
          <div
            className={`rounded-2xl px-4 py-3 ${
              isUser
                ? "bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-br-md shadow-lg shadow-primary-500/20"
                : "bg-white border border-surface-200 text-surface-800 rounded-bl-md shadow-sm"
            }`}
          >
            {/* Text Content */}
            {message.content && (
              <div
                className={`text-sm leading-relaxed whitespace-pre-wrap ${
                  isUser ? "text-white" : "text-surface-800"
                }`}
              >
                {renderContent(message.content)}
              </div>
            )}
          </div>
        </div>

        {/* Inline results for assistant messages */}
        {!isUser && (
          <div className="ml-10 mt-2 space-y-3">
            {message.foods && message.foods.length > 0 && (
              <FoodList foods={message.foods} />
            )}
            {message.restaurants && message.restaurants.length > 0 && (
              <RestaurantList restaurants={message.restaurants} />
            )}
          </div>
        )}

        {/* Follow-up suggestions */}
        {!isUser &&
          message.follow_up_suggestions &&
          message.follow_up_suggestions.length > 0 && (
            <div className="ml-10 mt-3 flex flex-wrap gap-2">
              {message.follow_up_suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => onSuggestionClick?.(suggestion)}
                  className="text-xs px-3 py-1.5 rounded-full bg-primary-50 text-primary-700 border border-primary-200 hover:bg-primary-100 hover:border-primary-300 transition-all duration-200 hover:shadow-sm active:scale-95"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}

        {/* Timestamp */}
        <p
          className={`text-[10px] text-surface-400 mt-1.5 ${
            isUser ? "text-right mr-10" : "ml-10"
          }`}
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
  // Simple bold markdown rendering
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
