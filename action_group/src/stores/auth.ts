import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { User } from '@/types'
import { authService } from '@/api/authService'
import { usersService } from '@/api/usersService'

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref<User | null>(null)
  const initialized = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => currentUser.value !== null)
  const isAdmin = computed(() => currentUser.value?.isAdmin === true)

  async function init() {
    if (initialized.value) return
    currentUser.value = await authService.restoreSession()
    initialized.value = true
  }

  async function login(login: string, password: string) {
    loading.value = true
    error.value = null
    try {
      currentUser.value = await authService.login(login, password)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Не удалось войти'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    await authService.logout()
    currentUser.value = null
  }

  /** Keep the session's user object fresh after profile edits elsewhere. */
  function refreshUser(user: User) {
    if (currentUser.value?.id === user.id) currentUser.value = user
  }

  async function updateMyNotifications(vkUserId: string | null) {
    const user = await usersService.updateMyNotifications(vkUserId)
    currentUser.value = user
    return user
  }

  async function sendTestNotification() {
    await usersService.sendTestNotification()
  }

  return {
    currentUser,
    initialized,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    init,
    login,
    logout,
    refreshUser,
    updateMyNotifications,
    sendTestNotification,
  }
})
