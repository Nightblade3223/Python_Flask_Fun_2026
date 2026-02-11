import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ForbiddenView from '../views/ForbiddenView.vue'

const routes = [
  { path: '/login', component: LoginView },
  { path: '/forbidden', component: ForbiddenView },
  { path: '/', component: DashboardView, meta: { requiresAuth: true } }
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (auth.token && !auth.user) await auth.fetchMe()
  if (to.meta.requiresAuth && !auth.token) return '/login'
  if (to.meta.permission && !auth.hasPerm(to.meta.permission)) return '/forbidden'
})

export default router
