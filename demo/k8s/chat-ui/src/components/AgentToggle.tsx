import { cn } from '@/lib/utils'
import type { AgentMode } from '@/types'
import { ShieldCheck, ShieldAlert } from 'lucide-react'

interface AgentToggleProps {
  mode: AgentMode
  onChange: (mode: AgentMode) => void
}

export function AgentToggle({ mode, onChange }: AgentToggleProps) {
  return (
    <div className="flex items-center gap-1 rounded-xl bg-muted p-1">
      <button
        onClick={() => onChange('safe')}
        className={cn(
          'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200',
          mode === 'safe'
            ? 'bg-white shadow-sm text-safe border border-safe/20'
            : 'text-muted-foreground hover:text-foreground'
        )}
      >
        <ShieldCheck className="h-4 w-4" />
        Safe Agent
      </button>
      <button
        onClick={() => onChange('compromised')}
        className={cn(
          'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200',
          mode === 'compromised'
            ? 'bg-white shadow-sm text-danger border border-danger/20'
            : 'text-muted-foreground hover:text-foreground'
        )}
      >
        <ShieldAlert className="h-4 w-4" />
        Compromised Agent
      </button>
    </div>
  )
}
