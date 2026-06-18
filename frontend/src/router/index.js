import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'persons',
        name: 'KeyPersonList',
        component: () => import('../views/KeyPersonList.vue'),
        meta: { title: '重点人员管理' },
      },
      {
        path: 'categories',
        name: 'PersonCategoryList',
        component: () => import('../views/PersonCategoryList.vue'),
        meta: { title: '人员类别管理' },
      },
      {
        path: 'tags',
        name: 'TagList',
        component: () => import('../views/TagList.vue'),
        meta: { title: '标签管理' },
      },
      {
        path: 'departments',
        name: 'DepartmentList',
        component: () => import('../views/DepartmentList.vue'),
        meta: { title: '部门管理', minRole: 'dept_admin' },
      },
      {
        path: 'users',
        name: 'UserList',
        component: () => import('../views/UserList.vue'),
        meta: { title: '用户管理', minRole: 'dept_admin' },
      },
      {
        path: 'logs',
        name: 'OperationLog',
        component: () => import('../views/OperationLog.vue'),
        meta: { title: '操作日志', minRole: 'dept_admin' },
      },
      {
        path: 'alerts',
        name: 'PersonAlertList',
        component: () => import('../views/PersonAlertList.vue'),
        meta: { title: '预警管理' },
      },
      {
        path: 'visit-tasks',
        name: 'VisitTaskList',
        component: () => import('../views/VisitTaskList.vue'),
        meta: { title: '走访任务管理' },
      },
      {
        path: 'visit-records/:taskId?',
        name: 'VisitRecordForm',
        component: () => import('../views/VisitRecordForm.vue'),
        meta: { title: '走访记录填报' },
      },
      {
        path: 'risk-assessment',
        name: 'RiskAssessmentPanel',
        component: () => import('../views/RiskAssessmentPanel.vue'),
        meta: { title: '风险评估' },
      },
      {
        path: 'notifications',
        name: 'NotificationList',
        component: () => import('../views/NotificationList.vue'),
        meta: { title: '通知中心' },
      },
      {
        path: 'lost-contact',
        name: 'LostContactTrack',
        component: () => import('../views/LostContactTrack.vue'),
        meta: { title: '失联追踪' },
      },
      {
        path: 'map',
        name: 'MapView',
        component: () => import('../views/MapView.vue'),
        meta: { title: '地图监控' },
      },
      {
        path: 'cross-region',
        name: 'CrossRegionTrackList',
        component: () => import('../views/CrossRegionTrackList.vue'),
        meta: { title: '流入流出管理' },
      },
      {
        path: 'devices',
        name: 'DeviceList',
        component: () => import('../views/DeviceList.vue'),
        meta: { title: '定位设备管理', minRole: 'dept_admin' },
      },
    ],
  },
  {
    path: '/print/:personId',
    name: 'PersonArchivePrint',
    component: () => import('../views/PersonArchivePrint.vue'),
    meta: { title: '电子档案打印' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const ROLE_LEVELS = { viewer: 1, operator: 2, dept_admin: 3, super_admin: 4 }

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && token) {
    next({ name: 'Dashboard' })
  } else if (to.meta?.minRole) {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    const userLevel = ROLE_LEVELS[user?.role] || 0
    const minLevel = ROLE_LEVELS[to.meta.minRole] || 0
    if (userLevel < minLevel) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
