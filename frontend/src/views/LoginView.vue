<template>
  <div class="card">
    <h2>Login</h2>
    <p v-if="error" style="color:red">{{ error }}</p>
    <input v-model="email" placeholder="email" />
    <input type="password" v-model="password" placeholder="password" />
    <label><input type="checkbox" v-model="remember" /> remember me</label>
    <button @click="submit">Sign in</button>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const email = ref('admin@example.com')
const password = ref('admin123!')
const remember = ref(true)
const error = ref('')

const submit = async () => {
  error.value = ''
  try {
    await auth.login(email.value, password.value, remember.value)
    router.push('/')
  } catch (e) {
    error.value = e.message
  }
}
</script>
