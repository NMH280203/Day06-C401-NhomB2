"use client";

import { useChat } from "@/hooks/useChat";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";

export function ChatWindow() {
  const { messages, isLoading, sendMessage } = useChat();

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} onSuggestionClick={sendMessage} />
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
