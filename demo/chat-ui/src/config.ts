export const AGENT_URLS = {
  safe: import.meta.env.VITE_SAFE_AGENT_URL ?? 'http://localhost:8082',
  compromised: import.meta.env.VITE_COMPROMISED_AGENT_URL ?? 'http://localhost:8083',
} as const
