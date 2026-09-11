import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { ScheduledMeeting } from '@/types'
import { scheduledMeetingsService } from '@/api/scheduledMeetingsService'

export const useScheduledMeetingsStore = defineStore('scheduledMeetings', () => {
  const items = ref<ScheduledMeeting[]>([])
  const loaded = ref(false)
  const loading = ref(false)

  async function fetchAll(force = false) {
    if (loaded.value && !force) return
    loading.value = true
    try {
      items.value = await scheduledMeetingsService.list()
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  function forUser(userId: string): ScheduledMeeting[] {
    return items.value
      .filter((m) => m.employeeId === userId)
      .sort((a, b) => a.scheduledDate.localeCompare(b.scheduledDate))
  }

  async function create(data: { employeeId: string; scheduledDate: string; note: string }) {
    const meeting = await scheduledMeetingsService.create(data)
    items.value.push(meeting)
    return meeting
  }

  async function remove(id: string) {
    await scheduledMeetingsService.remove(id)
    items.value = items.value.filter((m) => m.id !== id)
  }

  return { items, loaded, loading, fetchAll, forUser, create, remove }
})
