import { reactive } from 'vue'

interface ConfirmRequest {
  title: string
  message: string
  confirmLabel: string
  danger: boolean
  resolve: (value: boolean) => void
}

export const confirmState = reactive<{ request: ConfirmRequest | null }>({ request: null })

interface ConfirmOptions {
  title?: string
  confirmLabel?: string
  danger?: boolean
}

export function useConfirm() {
  function confirm(message: string, options: ConfirmOptions = {}): Promise<boolean> {
    return new Promise((resolve) => {
      confirmState.request = {
        title: options.title ?? 'Подтверждение',
        message,
        confirmLabel: options.confirmLabel ?? 'Подтвердить',
        danger: options.danger ?? false,
        resolve,
      }
    })
  }

  return { confirm }
}
