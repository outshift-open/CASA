import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { AgentMode } from '@/types'
import { ShieldCheck, ShieldAlert } from 'lucide-react'

interface AgentToggleProps {
  mode: AgentMode
  onChange: (mode: AgentMode) => void
}

export function AgentToggle({ mode, onChange }: AgentToggleProps) {
  return (
    <Tabs value={mode} onValueChange={(v) => onChange(v as AgentMode)}>
      <TabsList>
        <TabsTrigger
          value="safe"
          className="data-[state=active]:text-safe data-[state=active]:border data-[state=active]:border-safe/20"
        >
          <ShieldCheck className="h-3.5 w-3.5" />
          Safe Agent
        </TabsTrigger>
        <TabsTrigger
          value="compromised"
          className="data-[state=active]:text-danger data-[state=active]:border data-[state=active]:border-danger/20"
        >
          <ShieldAlert className="h-3.5 w-3.5" />
          Compromised Agent
        </TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
