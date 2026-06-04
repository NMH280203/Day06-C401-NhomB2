import React from 'react'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { useChat } from '../../hooks/useChat'

export function ChatWindow() {
  const { messages, isLoading, sendMessage } = useChat()

  return (
    <div className="flex flex-col h-full bg-slate-950/20 backdrop-blur-md">
      <MessageList messages={messages} onSendSuggestion={sendMessage} />
      <div className="p-4 border-t border-slate-900 bg-slate-950/30 flex-shrink-0">
        <MessageInput onSendMessage={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  )
}
