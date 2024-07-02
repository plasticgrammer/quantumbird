import { createRouter, createWebHistory } from 'vue-router'
import WeeklyReport from '../components/WeeklyReport.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: WeeklyReport
  },
  {
    path: '/report/:startDate',
    name: 'WeeklyReport',
    component: WeeklyReport
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router