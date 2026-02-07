import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const ADMIN_TOKEN_KEY = 'admin_token'

interface RouteMeta {
  requiresAuth?: boolean
  title?: string
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '仪表盘' }
      },
      // 文章管理
      {
        path: 'articles',
        name: 'ArticleList',
        component: () => import('@/views/articles/ArticleList.vue'),
        meta: { title: '文章列表' }
      },
      {
        path: 'articles/create',
        name: 'ArticleCreate',
        component: () => import('@/views/articles/ArticleCreate.vue'),
        meta: { title: '创建文章' }
      },
      {
        path: 'articles/:id/edit',
        name: 'ArticleEdit',
        component: () => import('@/views/articles/ArticleEdit.vue'),
        meta: { title: '编辑文章' }
      },
      // 题目管理
      {
        path: 'questions',
        name: 'QuestionList',
        component: () => import('@/views/questions/QuestionList.vue'),
        meta: { title: '题目列表' }
      },
      {
        path: 'questions/create',
        name: 'QuestionCreate',
        component: () => import('@/views/questions/QuestionCreate.vue'),
        meta: { title: '创建题目' }
      },
      {
        path: 'questions/:id/edit',
        name: 'QuestionEdit',
        component: () => import('@/views/questions/QuestionEdit.vue'),
        meta: { title: '编辑题目' }
      },
      // 用户管理
      {
        path: 'users',
        name: 'UserList',
        component: () => import('@/views/users/UserList.vue'),
        meta: { title: '用户列表' }
      },
      {
        path: 'users/:id',
        name: 'UserDetail',
        component: () => import('@/views/users/UserDetail.vue'),
        meta: { title: '用户详情' }
      },
      // 系统设置
      {
        path: 'settings/tags',
        name: 'TagList',
        component: () => import('@/views/settings/TagList.vue'),
        meta: { title: '标签管理' }
      },
      {
        path: 'settings/badges',
        name: 'BadgeList',
        component: () => import('@/views/settings/BadgeList.vue'),
        meta: { title: '勋章管理' }
      },
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem(ADMIN_TOKEN_KEY)

  if (to.meta.requiresAuth !== false && !token) {
    if (to.path !== '/login') {
      next('/login')
    } else {
      next()
    }
  } else if (to.path === '/login' && token) {
    if (from.path !== '/dashboard') {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router