import { defineStore } from 'pinia'
import { api } from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: localStorage.getItem('token') || '', user: null, permissions: [] }),
  actions: {
    async login(email, password, remember_me) {
      const data = await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password, remember_me }) })
      this.token = data.token
      this.user = data.user
      this.permissions = data.user.permissions
      localStorage.setItem('token', this.token)
    },
    async fetchMe() {
      if (!this.token) return
      try {
        const data = await api('/api/auth/me')
        this.user = data.user
        this.permissions = data.user.permissions
      } catch {
        this.logout()
      }
    },
    hasPerm(perm) { return this.permissions.includes(perm) },
    logout() {
      this.token = ''
      this.user = null
      this.permissions = []
      localStorage.removeItem('token')
    }
  }
})
