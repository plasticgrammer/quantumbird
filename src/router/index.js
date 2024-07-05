import { createRouter, createWebHistory } from 'vue-router'
import WeeklyReport from '../components/WeeklyReport.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: WeeklyReport
  },
  {
    path: '/:weekParam',
    name: 'WeeklyReport',
    component: WeeklyReport,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router