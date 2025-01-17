import { createRouter, createWebHistory } from 'vue-router'
import { contextPath } from '@/config/environment'
import store from '@/store'
import SignIn from '@/views/SignIn.vue'
import Overview from '@/views/Overview.vue'
import Dashboard from '@/views/Dashboard.vue'
import WeeklyReport from '@/views/WeeklyReport.vue'
import WeeklyReview from '@/views/WeeklyReview.vue'
import WeeklyReportSummary from '@/views/WeeklyReportSummary.vue'
import OrganizationManagement from '@/views/OrganizationManagement.vue'
import OrganizationAccount from '@/views/OrganizationAccount.vue'
import ReportSetting from '@/views/ReportSetting.vue'

const routes = [
  {
    path: '/',
    name: 'Root',
    component: () => import('@/views/About.vue'),
    meta: { hideNavigation: true, hideMascot: true, fullWidth: true },
    beforeEnter: async (to, from, next) => {
      try {
        const token = await store.dispatch('auth/fetchAuthToken')
        if (token) {
          next('/admin')
        } else {
          next()
        }
      } catch (error) {
        next()
      }
    }
  },
  {
    path: '/signin',
    name: 'SignIn',
    component: SignIn,
    meta: { hideNavigation: true, hideMascot: true }
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: SignIn,
    meta: { hideNavigation: true, hideMascot: true }
  },
  {
    path: '/admin',
    name: 'Overview',
    component: Overview,
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
    path: '/admin/accounts',
    name: 'OrganizationAccount',
    component: OrganizationAccount,
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
    path: '/admin/report-setting',
    name: 'ReportSetting',
    component: ReportSetting,
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
    meta: { hideNavigation: true, hideAnimation: true }
  },
  {
    path: '/admin/member-reports/:memberUuid',
    name: 'MemberReports',
    component: () => import('@/views/MemberReports.vue'),
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/account-setting',
    name: 'AccountSetting',
    component: () => import('@/views/AccountSetting.vue')
  },
  {
    path: '/billing',
    name: 'Billing',
    component: () => import('@/views/Billing.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/member/mail/:memberUuid',
    name: 'MailConfirmed',
    component: () => import('@/views/MailConfirmed.vue'),
    props: true,
    meta: { hideNavigation: true, hideAnimation: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { hideNavigation: true, hideAnimation: true }
  }
]

const router = createRouter({
  history: createWebHistory(contextPath),
  routes
})

router.beforeEach(async (to, from, next) => {
  //store.dispatch('setLoading', true)
  if (to.matched.some(record => record.meta.requiresAuth)) {
    try {
      const token = await store.dispatch('auth/fetchAuthToken')
      if (token) {
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

router.afterEach(() => {
  //store.dispatch('setLoading', false)
})

export default router