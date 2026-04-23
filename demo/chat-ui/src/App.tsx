import { useState, useRef, useEffect, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Send, RotateCcw } from 'lucide-react'
import { ChatMessage } from '@/components/ChatMessage'
import { TypingIndicator } from '@/components/TypingIndicator'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { Message } from '@/types'
import { AGENT_URL } from '@/config'
import { sendChat } from '@/api/chat'
import type { ChatMessage as ApiChatMessage } from '@/api/chat'
import { toast } from 'sonner'
import { Tooltip } from '@/components/ui/tooltip'

let messageCounter = 0
function nextId() {
  return `msg-${++messageCounter}`
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const mutation = useMutation({
    mutationFn: ({ apiMessages }: { apiMessages: ApiChatMessage[]; snapshot: Message[] }) =>
      sendChat(apiMessages),
    onSuccess: (data, { snapshot }) => {
      const agentMsg: Message = {
        id: nextId(),
        role: 'agent',
        content: data.response,
        conversation: data.conversation,
        timestamp: new Date(),
      }
      setMessages([...snapshot, agentMsg])
    },
    onError: (_, { snapshot }) => {
      setMessages(snapshot.map((m, i) => i === snapshot.length - 1 ? { ...m, error: true } : m))
    },
  })

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, mutation.isPending])

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = '0px'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }, [input])

  const sendMessage = useCallback(() => {
    const text = input.trim()
    if (!text || mutation.isPending) return

    setInput('')

    const userMsg: Message = {
      id: nextId(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    }
    const nextMessages = [...messages, userMsg]
    setMessages(nextMessages)

    const apiMessages: ApiChatMessage[] = nextMessages
      .filter((m) => !m.error)
      .map(({ role, content }) => ({
        role: role === 'agent' ? 'assistant' : role,
        content,
      }))

    mutation.mutate({ apiMessages, snapshot: nextMessages })
  }, [input, mutation, messages])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        sendMessage()
      }
    },
    [sendMessage]
  )

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background">
      <header className="shrink-0 flex items-center justify-between border-b border-border bg-white/80 backdrop-blur px-6 py-4 z-10">
        <div>
          <h1 className="text-lg font-semibold text-foreground tracking-tight">ZTA Chat Demo</h1>
          <p className="text-xs text-slate-400 font-mono mt-0.5">{AGENT_URL}/chat</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-lg bg-safe-muted px-3 py-1.5 text-xs font-medium text-safe">
            <span className="inline-block h-2 w-2 rounded-full bg-safe shrink-0" />
            ZTA authorization enforced
          </div>
          <Tooltip content="Clear conversation">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => { setMessages([]); setInput(''); toast.success('Conversation cleared') }}
            >
              <RotateCcw className="h-4 w-4" />
            </Button>
          </Tooltip>
        </div>
      </header>

      <ScrollArea className="flex-1 min-h-0">
        <div className="mx-auto max-w-2xl flex flex-col gap-4 px-6 py-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center gap-6">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl text-3xl bg-safe-muted">
                🏦
              </div>
              <div className="flex flex-col gap-2">
                <h2 className="text-xl font-semibold text-foreground">Welcome to the <span className="text-safe">Finance Agent</span></h2>
                <p className="text-sm text-slate-500 max-w-sm">
                  This agent has access to your banking tools. Every tool call is authorized by ZTA before execution.
                </p>
              </div>
              <div className="flex flex-col gap-2 w-full max-w-sm">
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">Try asking</p>
                {[
                  'What is my account balance?',
                  'Show me my savings accounts',
                  'Transfer $100 to my savings',
                ].map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => setInput(prompt)}
                    className="text-left text-sm px-4 py-2.5 rounded-xl border border-border bg-white hover:bg-safe-muted hover:border-safe/40 text-slate-700 transition-colors"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {mutation.isPending && <TypingIndicator />}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <footer className="shrink-0 border-t border-border bg-white/80 backdrop-blur px-6 py-4">
        <div className="mx-auto max-w-2xl flex items-end gap-3">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Send a message… (Enter to send, Shift+Enter for newline)"
            rows={1}
            disabled={mutation.isPending}
            className="flex-1 transition-[border-color,box-shadow] focus-visible:ring-safe/40"
          />
          <Button
            onClick={sendMessage}
            disabled={!input.trim() || mutation.isPending}
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
