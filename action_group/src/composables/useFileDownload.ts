import { http } from '@/api/http'
import { useToast } from './useToast'

export function useFileDownload() {
  const toast = useToast()

  async function download(url: string, filename: string) {
    try {
      const response = await http.get(url, { responseType: 'blob' })
      const blobUrl = URL.createObjectURL(response.data as Blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(blobUrl)
    } catch {
      toast.error('Не удалось скачать файл')
    }
  }

  return { download }
}
