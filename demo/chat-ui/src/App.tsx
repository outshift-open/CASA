import { useState, useRef, useEffect, useCallback } from 'react'
import { Send } from 'lucide-react'
import { ChatMessage } from '@/components/ChatMessage'
import { TypingIndicator } from '@/components/TypingIndicator'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { Message } from '@/types'
import { AGENT_URL } from '@/config'

let messageCounter = 0
function nextId() {
  return `msg-${++messageCounter}`
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Auto-resize textarea up to 160px
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = '0px'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }, [input])

  const sendMessage = useCallback(async () => {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setError(null)

    const userMsg: Message = {
      id: nextId(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await fetch(`${AGENT_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text }),
      })

      if (!res.ok) throw new Error(`Agent returned ${res.status}`)

      const data = (await res.json()) as { response: string }
      const agentMsg: Message = {
        id: nextId(),
        role: 'agent',
        content: data.response,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, agentMsg])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reach agent')
    } finally {
      setLoading(false)
    }
  }, [input, loading])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        void sendMessage()
      }
    },
    [sendMessage]
  )

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background">
      {/* Header */}
      <header className="shrink-0 flex items-center justify-between border-b border-border bg-white/80 backdrop-blur px-6 py-4 z-10">
        <div>
          <h1 className="text-lg font-semibold text-foreground tracking-tight">ZTA Chat Demo</h1>
          <p className="text-xs text-muted-foreground font-mono mt-0.5">{AGENT_URL}/chat</p>
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-safe-muted px-3 py-1.5 text-xs font-medium text-safe">
          <span className="inline-block h-2 w-2 rounded-full bg-safe shrink-0" />
          ZTA authorization enforced
        </div>
      </header>

      {/* Messages */}
      <ScrollArea className="flex-1 min-h-0">
        <div className="mx-auto max-w-2xl flex flex-col gap-4 px-6 py-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center gap-3">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl text-2xl bg-safe-muted">
                🛡️
              </div>
              <p className="text-sm text-muted-foreground max-w-xs">
                Chat with the agent. All tool calls are verified by ZTA.
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {loading && <TypingIndicator />}

          {error && (
            <div className="rounded-lg border border-danger/30 bg-danger-muted px-4 py-3 text-sm text-danger animate-fade-in">
              {error}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <footer className="shrink-0 border-t border-border bg-white/80 backdrop-blur px-6 py-4">
        <div className="mx-auto max-w-2xl flex items-end gap-3">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Send a message… (Enter to send, Shift+Enter for newline)"
            rows={1}
            disabled={loading}
            className="flex-1 transition-[border-color,box-shadow] focus-visible:ring-safe/40"
          />
          <Button
            onClick={() => void sendMessage()}
            disabled={!input.trim() || loading}
            variant="safe"
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </footer>
    </div>
  )
}
