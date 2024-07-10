import { createRouter, createWebHistory } from 'vue-router'
import WeeklyReport from '../components/WeeklyReport.vue'
import WeeklyReview from '../components/WeeklyReview.vue'
import OrganizationManagement from '../components/OrganizationManagement.vue'

const routes = [
  {
    path: '/',
    name: 'OrganizationManagement',
    component: OrganizationManagement
  },
  {
    path: '/report',
    name: 'WeekSelector',
    component: WeeklyReport
  },
  {
    path: '/report/:weekParam',
    name: 'WeeklyReport',
    component: WeeklyReport,
    props: true
  },
  {
    path: '/review',
    name: 'WeeklyReview',
    component: WeeklyReview
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router