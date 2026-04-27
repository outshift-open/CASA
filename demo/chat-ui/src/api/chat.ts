import { apiClient } from './client'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatResponse {
  response: string
  conversation: { messages: ChatMessage[] }
}

export async function sendChat(messages: ChatMessage[]): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/chat', {
    conversation: { messages },
  })
  return data
}
