"use client";

import { useCallback } from "react";
import { useChatStore } from "@/store/chatStore";
import { sendMessage } from "@/lib/api";
import { mergeContextFromMessage } from "@/lib/contextParser";
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
    pendingAskField,
    setContext,
    setPendingAskField,
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

      // 4. Cập nhật context từ tin nhắn (budget, vị trí, bữa ăn...)
      const mergedContext = mergeContextFromMessage(
        context,
        text.trim(),
        pendingAskField
      );
      setContext(mergedContext);
      setPendingAskField(null);

      // 5. Prepare all messages for payload
      const allMessages = [...messages, userMsg];

      try {
        await sendMessage(
          { messages: allMessages, context: mergedContext },
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
              appendToLastAssistantContent(delta);
            },
            onAskContext: (field, message, missingFields) => {
              setPendingAskField(field);
              updateLastAssistantMessage({
                content: message,
                status: undefined,
                ask_field: field,
                missing_context: missingFields,
              });
            },
            onDone: (follow_up_suggestions) => {
              updateLastAssistantMessage({
                follow_up_suggestions,
                status: undefined,
              });
            },
            onError: (errorMsg) => {
              updateLastAssistantMessage({
                content: errorMsg,
                status: undefined,
              });
            },
          }
        );
      } finally {
        setLoading(false);
        setStatus("");
      }
    },
    [
      messages,
      context,
      isLoading,
      results,
      pendingAskField,
      setContext,
      setPendingAskField,
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
