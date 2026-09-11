import axios from 'axios'

// Default baseURL works unchanged in dev (Vite proxy) and prod (nginx),
// both proxying /api to the backend — see vite.config.ts / nginx.conf.
export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const raw = localStorage.getItem('prz:v1:session')
  if (raw) {
    try {
      const { token } = JSON.parse(raw) as { token: string }
      config.headers.Authorization = `Bearer ${token}`
    } catch {
      // ignore malformed session
    }
  }
  return config
})

// Promote FastAPI's {"detail": "..."} into error.message so existing
// `e instanceof Error ? e.message : ...` call sites show it as-is.
http.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error?.response?.data?.detail
    if (typeof detail === 'string') {
      error.message = detail
    }
    return Promise.reject(error)
  },
)
