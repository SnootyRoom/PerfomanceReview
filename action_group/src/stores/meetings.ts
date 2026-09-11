import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Meeting } from '@/types'
import { meetingsService, type MeetingInput } from '@/api/meetingsService'

export const useMeetingsStore = defineStore('meetings', () => {
  const items = ref<Meeting[]>([])
  const loaded = ref(false)
  const loading = ref(false)

  async function fetchAll(force = false) {
    if (loaded.value && !force) return
    loading.value = true
    try {
      items.value = await meetingsService.list()
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  function forUser(userId: string): Meeting[] {
    return items.value.filter((m) => m.employeeId === userId).sort((a, b) => b.date.localeCompare(a.date))
  }

  async function create(data: MeetingInput) {
    const meeting = await meetingsService.create(data)
    items.value.push(meeting)
    return meeting
  }

  async function setProblemResolved(meetingId: string, problemId: string, resolved: boolean) {
    await meetingsService.setProblemResolved(meetingId, problemId, resolved)
    const meeting = items.value.find((m) => m.id === meetingId)
    const problem = meeting?.problems.find((p) => p.id === problemId)
    if (problem) {
      problem.resolved = resolved
      problem.resolvedAt = resolved ? new Date().toISOString().slice(0, 10) : null
    }
  }

  return { items, loaded, loading, fetchAll, forUser, create, setProblemResolved }
})
