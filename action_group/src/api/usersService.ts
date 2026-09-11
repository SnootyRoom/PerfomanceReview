import type { User } from '@/types'
import { http } from './http'

export interface CreateUserInput {
  fullName: string
  login: string
  password: string
  directionId: string
  departmentId: string | null
  isAdmin: boolean
}

export const usersService = {
  async list(): Promise<User[]> {
    const { data } = await http.get<User[]>('/users')
    return data
  },

  async create(input: CreateUserInput): Promise<User> {
    const { data } = await http.post<User>('/users', input)
    return data
  },

  async update(
    id: string,
    patch: Partial<Pick<User, 'fullName' | 'login' | 'directionId' | 'departmentId' | 'isAdmin'>> & {
      password?: string
    },
  ): Promise<User> {
    const { data } = await http.patch<User>(`/users/${id}`, patch)
    return data
  },

  async remove(id: string): Promise<void> {
    await http.delete(`/users/${id}`)
  },

  async updateMyNotifications(vkUserId: string | null): Promise<User> {
    const { data } = await http.patch<User>('/users/me/notifications', { vkUserId })
    return data
  },

  async sendTestNotification(): Promise<void> {
    await http.post('/users/me/notifications/test')
  },
}
