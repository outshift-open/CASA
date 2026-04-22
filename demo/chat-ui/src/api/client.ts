import axios from 'axios'
import { AGENT_URL } from '@/config'

export const apiClient = axios.create({
  baseURL: AGENT_URL,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-store, no-cache',
    'Pragma': 'no-cache',
  },
})
