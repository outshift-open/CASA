import { cn } from '@/lib/utils'
import type { Message } from '@/types'
import type { AgentMode } from '@/types'

interface ChatMessageProps {
  message: Message
  agentMode: AgentMode
}

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function ChatMessage({ message, agentMode }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div
      className={cn(
        'flex items-end gap-2 animate-fade-in',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      {!isUser && (
        <div
          className={cn(
            'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold',
            agentMode === 'safe'
              ? 'bg-safe-muted text-safe'
              : 'bg-danger-muted text-danger'
          )}
        >
          AI
        </div>
      )}

      <div className={cn('flex flex-col gap-1', isUser ? 'items-end' : 'items-start')}>
        <div
          className={cn(
            'max-w-[520px] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm',
            isUser
              ? 'rounded-br-sm bg-primary text-primary-foreground'
              : agentMode === 'safe'
              ? 'rounded-bl-sm bg-white border border-border text-foreground'
              : 'rounded-bl-sm bg-white border border-danger/30 text-foreground'
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
        <span className="text-[11px] text-muted-foreground px-1">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  )
}
