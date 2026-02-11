<template>
  <div>
    <div class="card"><h2>Welcome {{ auth.user?.email }}</h2><p>Permissions: {{ auth.permissions.join(', ') }}</p></div>

    <div v-if="auth.hasPerm('admin.panel')">
      <div class="card">
        <h3>Users</h3>
        <button @click="loadUsers">Refresh</button>
        <ul><li v-for="u in users" :key="u.id">{{ u.email }} | active: {{ u.is_active }}
          <button @click="toggleUser(u)">toggle active</button>
        </li></ul>
      </div>
      <div class="card">
        <h3>Groups</h3>
        <button @click="loadGroups">Refresh</button>
        <ul><li v-for="g in groups" :key="g.id">{{ g.name }} ({{ g.permissions.join(', ') }})</li></ul>
      </div>
    </div>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { api } from '../api/client'

const auth = useAuthStore()
const users = ref([])
const groups = ref([])

const loadUsers = async () => {
  const data = await api('/api/users')
  users.value = data.items
}
const loadGroups = async () => {
  const data = await api('/api/groups')
  groups.value = data.items
}
const toggleUser = async (u) => {
  await api(`/api/users/${u.id}`, { method: 'PATCH', body: JSON.stringify({ is_active: !u.is_active }) })
  await loadUsers()
}

onMounted(async () => {
  if (auth.hasPerm('admin.panel')) {
    await loadUsers()
    await loadGroups()
  }
})
</script>
