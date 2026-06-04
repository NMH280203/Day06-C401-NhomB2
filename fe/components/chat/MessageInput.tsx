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
    <div className="glass-navbar border-t border-white/20 p-4 sm:p-5">
      <div className="flex items-end gap-3 max-w-4xl mx-auto">
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
            className="w-full resize-none rounded-2xl px-5 py-3.5 pr-12 text-sm text-surface-900 placeholder:text-surface-400 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed glass-input"
          />
        </div>
        <button
          id="send-button"
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className="flex-shrink-0 w-12 h-12 rounded-2xl btn-glow flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed disabled:shadow-none active:scale-95"
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
