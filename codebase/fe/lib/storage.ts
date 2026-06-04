import type { Message, UserContext } from "./types";

const MESSAGES_KEY = "food-chat-messages";
const CONTEXT_KEY = "food-chat-context";

export function saveChat(messages: Message[]): void {
  try {
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
  } catch {
    console.warn("Failed to save chat to localStorage");
  }
}

export function loadChat(): Message[] {
  try {
    const raw = localStorage.getItem(MESSAGES_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as Message[];
  } catch {
    return [];
  }
}

export function saveContext(ctx: UserContext): void {
  try {
    localStorage.setItem(CONTEXT_KEY, JSON.stringify(ctx));
  } catch {
    console.warn("Failed to save context to localStorage");
  }
}

export function loadContext(): UserContext {
  try {
    const raw = localStorage.getItem(CONTEXT_KEY);
    if (!raw) return {};
    return JSON.parse(raw) as UserContext;
  } catch {
    return {};
  }
}
