"use client";

import { useRef, useEffect } from "react";
import type { Message } from "@/lib/types";
import { MessageBubble } from "./MessageBubble";

interface MessageListProps {
  messages: Message[];
  onSuggestionClick: (text: string) => void;
}

export function MessageList({ messages, onSuggestionClick }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md animate-fade-in">
          {/* Hero icon */}
          <div className="relative mx-auto w-24 h-24 mb-6">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-400 to-primary-600 rounded-3xl rotate-6 opacity-20 animate-pulse" />
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500 to-primary-600 rounded-3xl flex items-center justify-center shadow-xl shadow-primary-500/30">
              <span className="text-4xl">🍜</span>
            </div>
          </div>

          <h2 className="text-2xl font-bold bg-gradient-to-r from-surface-900 to-surface-600 bg-clip-text text-transparent mb-2">
            Xin chào! 👋
          </h2>
          <p className="text-surface-500 text-sm leading-relaxed mb-6">
            Mình là trợ lý gợi ý món ăn & nhà hàng AI. Hãy cho mình biết bạn
            muốn ăn gì, ở đâu, hoặc bất kỳ điều gì bạn thích nhé!
          </p>

          {/* Quick prompts */}
          <div className="flex flex-wrap justify-center gap-2">
            {[
              "Gợi ý bữa trưa ngon gần đây",
              "Món chay cho 2 người",
              "Quán cafe view đẹp",
              "Ăn gì tối nay?",
            ].map((prompt) => (
              <button
                key={prompt}
                onClick={() => onSuggestionClick(prompt)}
                className="text-xs px-4 py-2 rounded-full bg-white border border-surface-200 text-surface-600 hover:border-primary-300 hover:text-primary-600 hover:bg-primary-50 transition-all duration-200 shadow-sm hover:shadow-md active:scale-95"
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
    <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
      {messages.map((msg) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          onSuggestionClick={onSuggestionClick}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
