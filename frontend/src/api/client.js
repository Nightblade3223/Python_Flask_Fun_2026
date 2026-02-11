import { useAuthStore } from '../stores/auth'

export async function api(path, options = {}) {
  const auth = useAuthStore()
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (auth.token) headers.Authorization = `Bearer ${auth.token}`
  const resp = await fetch(path, { ...options, headers })
  const data = await resp.json().catch(() => ({}))
  if (!resp.ok) {
    const err = data.error?.message || 'Request failed'
    throw new Error(err)
  }
  return data
}
