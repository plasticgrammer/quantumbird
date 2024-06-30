import { createRouter, createWebHistory } from 'vue-router'
import WeekSelector from '../components/WeekSelector.vue'
import WeeklyReport from '../components/WeeklyReport.vue'

const routes = [
  {
    path: '/',
    name: 'WeekSelector',
    component: WeekSelector
  },
  {
    path: '/report/:startDate/:endDate',
    name: 'WeeklyReport',
    component: WeeklyReport
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router