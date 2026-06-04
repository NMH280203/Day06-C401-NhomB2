import { useChatStore } from './useChatStore'
import * as api from '../lib/api'
import { Message, FoodSuggestion, Restaurant } from '../lib/types'
import { saveChat } from '../lib/storage'
import { useEffect } from 'react'

export function useChat() {
  const messages = useChatStore((state) => state.messages)
  const context = useChatStore((state) => state.context)
  const isLoading = useChatStore((state) => state.isLoading)
  const currentStatus = useChatStore((state) => state.currentStatus)
  const results = useChatStore((state) => state.results)

  const addMessage = useChatStore((state) => state.addMessage)
  const updateLastAssistantMessage = useChatStore((state) => state.updateLastAssistantMessage)
  const setLoading = useChatStore((state) => state.setLoading)
  const setStatus = useChatStore((state) => state.setStatus)
  const setResults = useChatStore((state) => state.setResults)
  const clearHistory = useChatStore((state) => state.clearHistory)

  // Synchronize messages to storage when changed
  useEffect(() => {
    saveChat(messages)
  }, [messages])

  const send = async (text: string) => {
    if (!text.trim() || isLoading) return

    // 1. Tạo Message user, addMessage vào store
    const userMsg: Message = {
      id: Math.random().toString(36).substring(7),
      role: 'user',
      content: text,
      timestamp: Date.now(),
    }
    addMessage(userMsg)

    // 2. Tạo Message assistant rỗng, addMessage vào store
    const assistantMsg: Message = {
      id: Math.random().toString(36).substring(7),
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      status: 'Đang chuẩn bị...',
    }
    addMessage(assistantMsg)
    setLoading(true)

    let accumulatedText = ''
    let lastFoods: FoodSuggestion[] = []
    let lastRestaurants: Restaurant[] = []

    try {
      // 3. Gọi api.sendMessage với toàn bộ messages + context
      // Note: we fetch the messages list from store state directly to include the newly added ones
      const currentMessages = useChatStore.getState().messages

      await api.sendMessage(
        {
          messages: currentMessages,
          context,
        },
        {
          onThinking: (status) => {
            setStatus(status)
            updateLastAssistantMessage({ status })
          },
          onFoodResults: (foods) => {
            lastFoods = foods
            setResults(foods, [])
            updateLastAssistantMessage({ foods })
          },
          onRestaurantResults: (restaurants) => {
            lastRestaurants = restaurants
            setResults(lastFoods, restaurants)
            updateLastAssistantMessage({ restaurants })
          },
          onTextDelta: (delta) => {
            accumulatedText += delta
            updateLastAssistantMessage({ content: accumulatedText, status: undefined })
            setStatus('')
          },
          onAskContext: (field, askMsg) => {
            // "onAskContext → addMessage assistant với content = message"
            const askBubble: Message = {
              id: Math.random().toString(36).substring(7),
              role: 'assistant',
              content: askMsg,
              timestamp: Date.now(),
            }
            addMessage(askBubble)
          },
          onDone: (followUps) => {
            updateLastAssistantMessage({ follow_up_suggestions: followUps, status: undefined })
            setLoading(false)
            setStatus('')
          },
          onError: (errMsg) => {
            updateLastAssistantMessage({ content: errMsg, status: undefined })
            setLoading(false)
            setStatus('')
          },
        }
      )
    } catch (err) {
      console.error('Chat hook error:', err)
      updateLastAssistantMessage({
        content: 'Đã xảy ra lỗi khi kết nối với máy chủ AI.',
        status: undefined,
      })
      setLoading(false)
      setStatus('')
    }
  }

  return {
    messages,
    context,
    isLoading,
    currentStatus,
    results,
    sendMessage: send,
    clearHistory,
  }
}
