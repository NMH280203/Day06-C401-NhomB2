import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ChatStore, FoodSuggestion, Message, Restaurant, UserContext } from "@/lib/types";

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      messages: [],
      context: {},
      pendingAskField: null as string | null,
      isLoading: false,
      currentStatus: "",
      results: {
        foods: [],
        restaurants: [],
      },

      addMessage: (msg: Message) =>
        set((state) => ({
          messages: [...state.messages, msg],
        })),

      updateLastAssistantMessage: (patch: Partial<Message>) =>
        set((state) => {
          const messages = [...state.messages];
          for (let i = messages.length - 1; i >= 0; i--) {
            if (messages[i].role === "assistant") {
              messages[i] = { ...messages[i], ...patch };
              break;
            }
          }
          return { messages };
        }),

      setContext: (ctx: Partial<UserContext>) =>
        set((state) => ({
          context: { ...state.context, ...ctx },
        })),

      setPendingAskField: (field: string | null) => set({ pendingAskField: field }),

      setLoading: (v: boolean) => set({ isLoading: v }),

      setStatus: (s: string) => set({ currentStatus: s }),

      setResults: (foods: FoodSuggestion[], restaurants: Restaurant[]) =>
        set({ results: { foods, restaurants } }),

      appendToLastAssistantContent: (delta: string) =>
        set((state) => {
          const messages = [...state.messages];
          for (let i = messages.length - 1; i >= 0; i--) {
            if (messages[i].role === "assistant") {
              messages[i] = {
                ...messages[i],
                content: messages[i].content + delta,
                status: undefined,
              };
              break;
            }
          }
          return { messages };
        }),

      clearHistory: () =>
        set({
          messages: [],
          results: { foods: [], restaurants: [] },
          currentStatus: "",
          isLoading: false,
          pendingAskField: null,
        }),
    }),
    {
      name: "food-chat-store",
      partialize: (state) => ({
        messages: state.messages,
        context: state.context,
        results: state.results,
      }),
    }
  )
);
