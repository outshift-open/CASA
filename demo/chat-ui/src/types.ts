export interface Message {
  id: string
  role: 'user' | 'agent'
  content: string
  conversation?: { messages: unknown[] }
  timestamp: Date
}
