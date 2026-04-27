export interface Message {
  id: string
  role: 'user' | 'agent'
  content: string
  conversation?: { messages: unknown[] }
  error?: boolean
  timestamp: Date
}
