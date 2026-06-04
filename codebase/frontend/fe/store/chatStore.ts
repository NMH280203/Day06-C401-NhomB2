import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ChatStore, Message, UserContext, FoodSuggestion, Restaurant } from '../lib/types'

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      messages: [],
      context: {},
      isLoading: false,
      currentStatus: '',
      results: {
        foods: [],
        restaurants: [],
      },
      addMessage: (msg: Message) =>
        set((state) => ({ messages: [...state.messages, msg] })),
      updateLastAssistantMessage: (patch: Partial<Message>) =>
        set((state) => {
          const messages = [...state.messages]
          for (let i = messages.length - 1; i >= 0; i--) {
            if (messages[i].role === 'assistant') {
              messages[i] = { ...messages[i], ...patch }
              break
            }
          }
          return { messages }
        }),
      setContext: (ctx: Partial<UserContext>) =>
        set((state) => ({ context: { ...state.context, ...ctx } })),
      setLoading: (v: boolean) => set({ isLoading: v }),
      setStatus: (s: string) => set({ currentStatus: s }),
      setResults: (foods: FoodSuggestion[], restaurants: Restaurant[]) =>
        set((state) => ({
          results: {
            foods,
            restaurants: restaurants.length > 0 ? restaurants : state.results.restaurants,
          },
        })),
      clearHistory: () =>
        set({
          messages: [],
          results: { foods: [], restaurants: [] },
          currentStatus: '',
        }),
    }),
    {
      name: 'food-chat-store',
      // Only persist messages and context, as specified in FE.md
      partialize: (state) => ({
        messages: state.messages,
        context: state.context,
      }),
    }
  )
)
