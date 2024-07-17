import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import WeeklyReport from '../views/WeeklyReport.vue'
import WeeklyReview from '../views/WeeklyReview.vue'
import OrganizationManagement from '../views/OrganizationManagement.vue'

/*
1. 管理者向け

   組織管理画面:
   /admin/organizations

   週次報告確認画面:
   /admin/reports/{YYYY-Www}
   例: /admin/reports/2023-W25

2. 組織メンバー向け

   週次報告画面:
   /reports/{organizationId}/{memberUuid}/{YYYY-Www}
   例: /reports/abc123/550e8400-e29b-41d4-a716-446655440000/2023-W25

3. その他

   ログインページ:
   /login

   ダッシュボード（ログイン後のランディングページ）:
   /dashboard

   404 ページ:
   /404

   500 ページ:
   /500
*/
const routes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/admin/organization',
    name: 'OrganizationManagement',
    component: OrganizationManagement
  },
  {
    path: '/admin/reports',
    name: 'WeeklyReviewSelector',
    component: WeeklyReview
  },
  {
    path: '/admin/reports/:weekParam',
    name: 'WeeklyReview',
    component: WeeklyReview,
    props: true
  },
  {
    path: '/reports/:organizationId/:memberUuid',
    name: 'WeekReportSelector',
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

export default router