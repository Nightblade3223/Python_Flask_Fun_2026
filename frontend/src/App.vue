<template>
  <div class="layout">
    <header>
      <h1>RBAC Admin</h1>
      <button v-if="auth.token" @click="logout">Logout</button>
    </header>
    <main><router-view /></main>
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<style>
body { font-family: Arial, sans-serif; margin:0; }
.layout { max-width: 1000px; margin: 0 auto; padding: 12px; }
header { display:flex; justify-content: space-between; align-items:center; }
input, button, select { margin: 4px; padding: 6px; }
.card { border:1px solid #ddd; padding:12px; margin-bottom:12px; }
</style>
