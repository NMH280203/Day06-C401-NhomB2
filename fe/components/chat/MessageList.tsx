"use client";

import { useRef, useEffect } from "react";
import type { Message } from "@/lib/types";
import { MessageBubble } from "./MessageBubble";

interface MessageListProps {
  messages: Message[];
  onSuggestionClick: (text: string) => void;
  isLoading?: boolean;
}

export function MessageList({
  messages,
  onSuggestionClick,
  isLoading = false,
}: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md animate-scale-in">
          <div className="relative mx-auto w-28 h-28 mb-8 animate-float">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-400/20 to-accent-cyan/20 rounded-3xl rotate-6 blur-sm animate-blob" />
            <div className="absolute inset-0 glass-card flex items-center justify-center !rounded-3xl shadow-glow">
              <span className="text-5xl">🍜</span>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-gradient-cyan mb-3 animate-slide-down">
            Xin chào!
          </h2>
          <p className="text-surface-500 text-sm leading-relaxed mb-8 animate-fade-in">
            Mình là trợ lý gợi ý món ăn & nhà hàng AI. Hãy cho mình biết bạn
            muốn ăn gì, ở đâu, hoặc bất kỳ điều gì bạn thích nhé!
          </p>

          <div className="flex flex-wrap justify-center gap-2.5 stagger-children">
            {[
              "Gợi ý bữa trưa ngon gần đây",
              "Món chay cho 2 người",
              "Quán cafe view đẹp",
              "Ăn gì tối nay?",
            ].map((prompt) => (
              <button
                key={prompt}
                onClick={() => onSuggestionClick(prompt)}
                className="text-xs px-4 py-2.5 rounded-full glass-card !rounded-full text-surface-600 font-medium hover:text-primary-600 hover:shadow-glow-sm hover:scale-105 transition-all duration-300 active:scale-95"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
      {messages.map((msg, index) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          index={index}
          isLast={index === messages.length - 1}
          isLoading={isLoading}
          onSuggestionClick={onSuggestionClick}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
