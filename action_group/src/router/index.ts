import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
    },
    {
      path: '/employees',
      name: 'employees',
      component: () => import('@/views/EmployeesView.vue'),
    },
    {
      path: '/employees/:id',
      name: 'employee-profile',
      component: () => import('@/views/EmployeeProfileView.vue'),
      props: true,
    },
    {
      path: '/employees/:id/meetings/new',
      name: 'meeting-new',
      component: () => import('@/views/MeetingFormView.vue'),
      props: true,
    },
    {
      path: '/departments',
      name: 'departments',
      component: () => import('@/views/DepartmentsView.vue'),
      meta: { requiresAdmin: true },
    },
    {
      path: '/skills',
      name: 'skills-admin',
      component: () => import('@/views/SkillsAdminView.vue'),
      meta: { requiresAdmin: true },
    },
    {
      path: '/users',
      name: 'users-admin',
      component: () => import('@/views/UsersAdminView.vue'),
      meta: { requiresAdmin: true },
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('@/views/AnalyticsView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { public: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.initialized) await auth.init()

  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    useToast().error('Недостаточно прав для этого раздела')
    return { name: 'dashboard' }
  }

  return true
})

export default router
