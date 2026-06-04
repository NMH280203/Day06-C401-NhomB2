"use client";

import { useCallback } from "react";
import { useChatStore } from "@/store/chatStore";
import { mockSendMessage } from "@/lib/api";
import type { Message } from "@/lib/types";

function generateId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

export function useChat() {
  const {
    messages,
    context,
    isLoading,
    currentStatus,
    results,
    addMessage,
    updateLastAssistantMessage,
    appendToLastAssistantContent,
    setLoading,
    setStatus,
    setResults,
    clearHistory,
  } = useChatStore();

  const sendMsg = useCallback(
    async (text: string) => {
      if (!text.trim() || isLoading) return;

      // 1. Create & add user message
      const userMsg: Message = {
        id: generateId(),
        role: "user",
        content: text.trim(),
        timestamp: Date.now(),
      };
      addMessage(userMsg);

      // 2. Create & add empty assistant message
      const assistantMsg: Message = {
        id: generateId(),
        role: "assistant",
        content: "",
        timestamp: Date.now(),
      };
      addMessage(assistantMsg);

      // 3. Set loading
      setLoading(true);
      setStatus("");

      // 4. Prepare all messages for payload
      const allMessages = [...messages, userMsg];

      // 5. Call API with SSE callbacks
      // Using mock for now — swap to `sendMessage` from api.ts when BE is ready
      await mockSendMessage(
        { messages: allMessages, context },
        {
          onThinking: (status) => {
            setStatus(status);
            updateLastAssistantMessage({ status });
          },
          onFoodResults: (foods) => {
            setResults(foods, results.restaurants);
            updateLastAssistantMessage({ foods });
          },
          onRestaurantResults: (restaurants) => {
            setResults(results.foods, restaurants);
            updateLastAssistantMessage({ restaurants });
          },
          onTextDelta: (delta) => {
            // Append delta char to the last assistant message's content
            appendToLastAssistantContent(delta);
          },
          onAskContext: (_field, message) => {
            const askMsg: Message = {
              id: generateId(),
              role: "assistant",
              content: message,
              timestamp: Date.now(),
            };
            addMessage(askMsg);
          },
          onDone: (follow_up_suggestions) => {
            updateLastAssistantMessage({
              follow_up_suggestions,
              status: undefined,
            });
            setLoading(false);
            setStatus("");
          },
          onError: (errorMsg) => {
            updateLastAssistantMessage({
              content: `⚠️ ${errorMsg}`,
              status: undefined,
            });
            setLoading(false);
            setStatus("");
          },
        }
      );
    },
    [
      messages,
      context,
      isLoading,
      results,
      addMessage,
      updateLastAssistantMessage,
      appendToLastAssistantContent,
      setLoading,
      setStatus,
      setResults,
    ]
  );

  return {
    messages,
    isLoading,
    currentStatus,
    results,
    sendMessage: sendMsg,
    clearHistory,
  };
}
