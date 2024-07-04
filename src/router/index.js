// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import WeeklyReport from '@/components/WeeklyReport.vue'

const routes = [
  {
    path: '/',
    name: 'WeeklyReport',
    component: WeeklyReport,
    props: (route) => ({ weekParam: route.query.week })
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router