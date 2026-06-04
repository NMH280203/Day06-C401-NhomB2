"use client";

import { useChat } from "@/hooks/useChat";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";

export function ChatWindow() {
  const { messages, isLoading, sendMessage } = useChat();

  return (
    <div className="flex flex-col h-full relative">
      <MessageList
        messages={messages}
        onSuggestionClick={sendMessage}
        isLoading={isLoading}
      />
      <MessageInput onSend={sendMessage} disabled={isLoading} isLoading={isLoading} />
    </div>
  );
}
