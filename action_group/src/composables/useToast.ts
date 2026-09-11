import { reactive } from 'vue'

export type ToastKind = 'success' | 'error' | 'info'

interface Toast {
  id: number
  kind: ToastKind
  message: string
}

let nextId = 1
export const toasts = reactive<Toast[]>([])

function push(kind: ToastKind, message: string) {
  const id = nextId++
  toasts.push({ id, kind, message })
  setTimeout(() => {
    const idx = toasts.findIndex((t) => t.id === id)
    if (idx !== -1) toasts.splice(idx, 1)
  }, 4000)
}

export function useToast() {
  return {
    success: (message: string) => push('success', message),
    error: (message: string) => push('error', message),
    info: (message: string) => push('info', message),
  }
}
