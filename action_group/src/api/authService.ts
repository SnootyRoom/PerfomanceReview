import type { User } from '@/types'
import { http } from './http'

const SESSION_KEY = 'prz:v1:session'

interface StoredSession {
  userId: string
  token: string
}

export const authService = {
  async login(login: string, password: string): Promise<User> {
    const { data } = await http.post<{ token: string; user: User }>('/auth/login', { login, password })
    const session: StoredSession = { userId: data.user.id, token: data.token }
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))
    return data.user
  },

  async logout(): Promise<void> {
    localStorage.removeItem(SESSION_KEY)
  },

  async restoreSession(): Promise<User | null> {
    const raw = localStorage.getItem(SESSION_KEY)
    if (!raw) return null
    try {
      const { data } = await http.get<User>('/auth/me')
      return data
    } catch {
      localStorage.removeItem(SESSION_KEY)
      return null
    }
  },
}
