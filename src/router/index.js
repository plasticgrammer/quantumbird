import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'
import SignIn from '../views/SignIn.vue'
import Support from '../views/Support.vue'
import Dashboard from '../views/Dashboard.vue'
import WeeklyReport from '../views/WeeklyReport.vue'
import WeeklyReview from '../views/WeeklyReview.vue'
import WeeklyReportSummary from '../views/WeeklyReportSummary.vue'
import OrganizationManagement from '../views/OrganizationManagement.vue'
import RequestSetting from '../views/RequestSetting.vue'

const routes = [
  {
    path: '/',
    name: 'Root',
    component: SignIn,
    beforeEnter: async (to, from, next) => {
      try {
        const token = await store.dispatch('auth/fetchAuthToken')
        if (token) {
          next('/admin')
        } else {
          next({
            name: 'SignIn',
            query: { redirect: to.fullPath }
          })
        }
      } catch (error) {
        console.error('認証チェックエラー:', error)
        next({
          name: 'SignIn',
          query: { redirect: to.fullPath }
        })
      }
    }
  },
  {
    path: '/signin',
    name: 'SignIn',
    component: SignIn,
    meta: { hideNavigation: true }
  },
  {
    path: '/admin',
    name: 'Support',
    component: Support,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/dashboard',
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
    path: '/admin/reports/:weekString',
    name: 'WeeklyReview',
    component: WeeklyReview,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/request-setting',
    name: 'RequestSetting',
    component: RequestSetting,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/reports/:organizationId/:memberUuid',
    name: 'WeeklyReportSelector',
    component: WeeklyReport,
    props: true,
    meta: { hideNavigation: true }
  },
  {
    path: '/reports/:organizationId/:memberUuid/:weekString',
    name: 'WeeklyReport',
    component: WeeklyReport,
    props: true,
    meta: { hideNavigation: true }
  },
  {
    path: '/view/:token',
    name: 'WeeklyReportSummary',
    component: WeeklyReportSummary,
    props: true,
    meta: { hideNavigation: true }
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    try {
      const token = await store.dispatch('auth/fetchAuthToken')
      if (token) {
        // トークンが取得できた場合、ユーザー情報も取得
        await store.dispatch('auth/fetchUser')
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