declare global {
  interface Window {
    __ENV__?: { AGENT_URL?: string }
  }
}

export const AGENT_URL = window.__ENV__?.AGENT_URL ?? import.meta.env.VITE_AGENT_URL ?? '/safe-agent'
