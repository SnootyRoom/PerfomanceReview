import { ref } from 'vue'
import { http } from '@/api/http'

export function useAiAnalysis(endpoint: string) {
  const show = ref(false)
  const loading = ref(false)
  const error = ref('')
  const text = ref('')

  async function open() {
    show.value = true
    loading.value = true
    error.value = ''
    text.value = ''
    try {
      const { data } = await http.post<{ text: string }>(endpoint)
      text.value = data.text
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Не удалось получить анализ'
    } finally {
      loading.value = false
    }
  }

  return { show, loading, error, text, open }
}
