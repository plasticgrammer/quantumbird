import { createRouter, createWebHistory } from 'vue-router'
import { getCurrentUser } from '@aws-amplify/auth'
import Dashboard from '../views/Dashboard.vue'
import SignIn from '../views/SignIn.vue'
import WeeklyReport from '../views/WeeklyReport.vue'
import WeeklyReview from '../views/WeeklyReview.vue'
import OrganizationManagement from '../views/OrganizationManagement.vue'

const routes = [
  {
    path: '/signin',
    name: 'SignIn',
    component: SignIn
  },
  {
    path: '/admin',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/organization',
    name: 'OrganizationManagement',
    component: OrganizationManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/reports',
    name: 'WeeklyReviewSelector',
    component: WeeklyReview,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/reports/:weekParam',
    name: 'WeeklyReview',
    component: WeeklyReview,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/reports/:organizationId/:memberUuid',
    name: 'WeeklyReportSelector',
    component: WeeklyReport,
    props: true
  },
  {
    path: '/reports/:organizationId/:memberUuid/:weekString',
    name: 'WeeklyReport',
    component: WeeklyReport,
    props: true
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  // const moveToSignIn = to.name == 'Login' && Object.keys(to.query).length == 0
  if (to.matched.some(record => record.meta.requiresAuth)) {
    try {
      const user = await getCurrentUser()
      if (user) {
        // ユーザーが認証されている場合、要求されたルートに進む
        next()
      } else {
        // ユーザーが認証されていない場合、サインインページにリダイレクト
        next({
          name: 'SignIn',
          query: { redirect: to.fullPath }
        })
      }
    } catch (error) {
      console.error('認証チェックエラー:', error)
      // エラーが発生した場合、サインインページにリダイレクト
      next({
        name: 'SignIn',
        query: { redirect: to.fullPath }
      })
    }
  } else {
    // 認証が不要なルートの場合、そのまま進む
    next()
  }
})

export default router