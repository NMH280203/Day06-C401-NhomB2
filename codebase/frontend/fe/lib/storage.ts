import { Message, UserContext } from './types'

export function saveChat(messages: Message[]): void {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem('food-chat-messages', JSON.stringify(messages))
  } catch (error) {
    console.error('Error saving chat to localStorage:', error)
  }
}

export function loadChat(): Message[] {
  if (typeof window === 'undefined') return []
  try {
    const data = window.localStorage.getItem('food-chat-messages')
    return data ? JSON.parse(data) : []
  } catch (error) {
    console.error('Error loading chat from localStorage:', error)
    return []
  }
}

export function saveContext(ctx: UserContext): void {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem('food-chat-context', JSON.stringify(ctx))
  } catch (error) {
    console.error('Error saving context to localStorage:', error)
  }
}

export function loadContext(): UserContext {
  if (typeof window === 'undefined') return {}
  try {
    const data = window.localStorage.getItem('food-chat-context')
    return data ? JSON.parse(data) : {}
  } catch (error) {
    console.error('Error loading context from localStorage:', error)
    return {}
  }
}
