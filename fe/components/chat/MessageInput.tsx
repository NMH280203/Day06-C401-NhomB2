"use client";

import { useState, useRef, useEffect, useCallback } from "react";

interface MessageInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, disabled = false }: MessageInputProps) {
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "auto";
    const maxHeight = 4 * 24; // 4 lines × ~24px
    textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
  }, []);

  useEffect(() => {
    adjustHeight();
  }, [text, adjustHeight]);

  const handleSend = useCallback(() => {
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [text, disabled, onSend]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  return (
    <div className="border-t border-surface-200 bg-white/80 backdrop-blur-xl p-3 sm:p-4">
      <div className="flex items-end gap-2 max-w-4xl mx-auto">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            id="message-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Bạn muốn ăn gì hôm nay? 🍜"
            disabled={disabled}
            rows={1}
            className="w-full resize-none rounded-2xl border border-surface-200 bg-surface-50 px-4 py-3 pr-12 text-sm text-surface-900 placeholder:text-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          />
        </div>
        <button
          id="send-button"
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className="flex-shrink-0 w-11 h-11 rounded-xl bg-gradient-to-r from-primary-500 to-primary-600 text-white flex items-center justify-center hover:from-primary-600 hover:to-primary-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 active:scale-95 shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40"
          aria-label="Gửi tin nhắn"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
