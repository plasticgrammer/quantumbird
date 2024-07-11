import { createRouter, createWebHistory } from 'vue-router'
import WeeklyReport from '../views/WeeklyReport.vue'
import WeeklyTeamReview from '../views/WeeklyTeamReview.vue'
import TeamManagement from '../views/TeamManagement.vue'

const routes = [
  {
    path: '/',
    name: 'TeamManagement',
    component: TeamManagement
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
    name: 'WeeklyTeamReview',
    component: WeeklyTeamReview
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router