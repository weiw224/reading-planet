# Phase 3: 管理后台前端开发 (Vue 3 + Element Plus)

> **预估工时**: 5-7 人天  
> **前置依赖**: Phase 2.4 (管理后台 API)  
> **产出物**: 完整的管理后台 Web 应用

---

## 3.1 目标概述

本阶段完成管理后台前端开发，包括：
- 登录与权限控制
- 仪表盘数据展示
- 文章管理（列表、创建、编辑、发布）
- 题目管理（列表、创建、编辑）
- 用户管理（列表、查看）
- 系统配置（标签、勋章）

---

## 3.2 项目结构

```
admin/
├── src/
│   ├── api/                  # API 调用
│   │   ├── index.ts          # Axios 实例
│   │   ├── auth.ts           # 认证接口
│   │   ├── articles.ts       # 文章接口
│   │   ├── questions.ts      # 题目接口
│   │   ├── users.ts          # 用户接口
│   │   ├── tags.ts           # 标签接口
│   │   └── dashboard.ts      # 仪表盘接口
│   │
│   ├── components/           # 公共组件
│   │   ├── AppHeader.vue     # 顶部导航
│   │   ├── AppSidebar.vue    # 侧边栏
│   │   ├── TagSelect.vue     # 标签选择器
│   │   ├── AbilitySelect.vue # 能力选择器
│   │   └── RichEditor.vue    # 富文本编辑器
│   │
│   ├── composables/          # 组合式函数
│   │   ├── useAuth.ts        # 认证相关
│   │   ├── usePagination.ts  # 分页
│   │   └── useMessage.ts     # 消息提示
│   │
│   ├── layouts/
│   │   ├── DefaultLayout.vue # 默认布局
│   │   └── BlankLayout.vue   # 空白布局（登录页）
│   │
│   ├── router/
│   │   └── index.ts          # 路由配置
│   │
│   ├── stores/
│   │   ├── auth.ts           # 认证状态
│   │   └── app.ts            # 应用状态
│   │
│   ├── styles/
│   │   ├── variables.scss    # SCSS 变量
│   │   └── global.scss       # 全局样式
│   │
│   ├── views/
│   │   ├── login/
│   │   │   └── LoginView.vue
│   │   ├── dashboard/
│   │   │   └── DashboardView.vue
│   │   ├── articles/
│   │   │   ├── ArticleList.vue
│   │   │   ├── ArticleCreate.vue
│   │   │   └── ArticleEdit.vue
│   │   ├── questions/
│   │   │   ├── QuestionList.vue
│   │   │   ├── QuestionCreate.vue
│   │   │   └── QuestionEdit.vue
│   │   ├── users/
│   │   │   ├── UserList.vue
│   │   │   └── UserDetail.vue
│   │   └── settings/
│   │       ├── TagList.vue
│   │       └── BadgeList.vue
│   │
│   ├── App.vue
│   └── main.ts
│
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 3.3 环境配置

### 3.3.1 package.json

```json
{
  "name": "reading-planet-admin",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "element-plus": "^2.5.0",
    "@element-plus/icons-vue": "^2.3.1",
    "axios": "^1.6.0",
    "dayjs": "^1.11.10",
    "@vueup/vue-quill": "^1.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "vue-tsc": "^1.8.0",
    "sass": "^1.69.0",
    "@types/node": "^20.10.0",
    "eslint": "^8.56.0",
    "eslint-plugin-vue": "^9.19.0",
    "@typescript-eslint/parser": "^6.0.0",
    "unplugin-auto-import": "^0.17.0",
    "unplugin-vue-components": "^0.26.0"
  }
}
```

### 3.3.2 vite.config.ts

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      imports: ['vue', 'vue-router', 'pinia'],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 3.3.3 环境变量 (.env.development)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=阅读星球管理后台
```

---

## 3.4 API 封装

### 3.4.1 Axios 实例 (api/index.ts)

```typescript
import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL + '/api/v1',
  timeout: 30000,
})

// 请求拦截器
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data } = response
    if (data.code === 0) {
      return data.data
    } else {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
  },
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      const message = (error.response?.data as any)?.detail || '请求失败'
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export default api
```

### 3.4.2 认证接口 (api/auth.ts)

```typescript
import api from './index'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  expires_in: number
}

export const login = (params: LoginParams): Promise<LoginResponse> => {
  return api.post('/auth/admin-login', params)
}
```

### 3.4.3 文章接口 (api/articles.ts)

```typescript
import api from './index'

export interface Article {
  id: number
  title: string
  content: string
  source_book?: string
  source_chapter?: string
  is_excerpt: boolean
  word_count: number
  reading_time: number
  article_difficulty: number
  status: string
  is_ai_generated: boolean
  created_at: string
  updated_at: string
  tags: Array<{ id: number; name: string; category: string }>
  question_count: number
}

export interface ArticleListParams {
  page?: number
  page_size?: number
  status?: string
  keyword?: string
}

export interface ArticleListResponse {
  items: Article[]
  total: number
  page: number
  page_size: number
}

export interface ArticleCreateParams {
  title: string
  content: string
  source_book?: string
  source_chapter?: string
  is_excerpt?: boolean
  article_difficulty: number
  tag_ids: number[]
}

export const getArticleList = (params: ArticleListParams): Promise<ArticleListResponse> => {
  return api.get('/admin/articles/', { params })
}

export const getArticle = (id: number): Promise<Article> => {
  return api.get(`/admin/articles/${id}`)
}

export const createArticle = (data: ArticleCreateParams): Promise<Article> => {
  return api.post('/admin/articles/', data)
}

export const updateArticle = (id: number, data: Partial<ArticleCreateParams>): Promise<Article> => {
  return api.put(`/admin/articles/${id}`, data)
}

export const deleteArticle = (id: number): Promise<void> => {
  return api.delete(`/admin/articles/${id}`)
}

export const publishArticle = (id: number): Promise<void> => {
  return api.post(`/admin/articles/${id}/publish`)
}

export const archiveArticle = (id: number): Promise<void> => {
  return api.post(`/admin/articles/${id}/archive`)
}
```

### 3.4.4 仪表盘接口 (api/dashboard.ts)

```typescript
import api from './index'

export interface DashboardStats {
  total_users: number
  active_users_today: number
  active_users_week: number
  total_articles: number
  published_articles: number
  total_questions: number
  total_readings: number
  checkins_today: number
}

export const getDashboardStats = (): Promise<DashboardStats> => {
  return api.get('/admin/dashboard/')
}
```

---

## 3.5 路由配置 (router/index.ts)

```typescript
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
```

---

## 3.6 状态管理 (stores/auth.ts)

```typescript
import { defineStore } from 'pinia'
import { login as loginApi, LoginParams } from '@/api/auth'
import router from '@/router'

interface AuthState {
  token: string | null
  username: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('admin_token'),
    username: localStorage.getItem('admin_username'),
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  
  actions: {
    async login(params: LoginParams) {
      const data = await loginApi(params)
      this.token = data.access_token
      this.username = params.username
      localStorage.setItem('admin_token', data.access_token)
      localStorage.setItem('admin_username', params.username)
      router.push('/dashboard')
    },
    
    logout() {
      this.token = null
      this.username = null
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_username')
      router.push('/login')
    },
  },
})
```

---

## 3.7 页面组件

### 3.7.1 登录页 (views/login/LoginView.vue)

```vue
<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="title">阅读星球管理后台</h1>
      
      <el-form 
        ref="formRef"
        :model="form" 
        :rules="rules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate()
  if (!valid) return
  
  loading.value = true
  try {
    await authStore.login(form)
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.title {
  text-align: center;
  margin-bottom: 40px;
  color: #333;
  font-size: 24px;
}

.login-btn {
  width: 100%;
}
</style>
```

### 3.7.2 仪表盘 (views/dashboard/DashboardView.vue)

```vue
<template>
  <div class="dashboard">
    <h2 class="page-title">仪表盘</h2>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card users">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_users }}</div>
            <div class="stat-label">总用户数</div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card articles">
          <div class="stat-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.published_articles }}</div>
            <div class="stat-label">已发布文章</div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card readings">
          <div class="stat-icon">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_readings }}</div>
            <div class="stat-label">总阅读量</div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="stat-card checkins">
          <div class="stat-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.checkins_today }}</div>
            <div class="stat-label">今日打卡</div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 更多统计 -->
    <el-row :gutter="20" class="more-stats">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>活跃用户</span>
          </template>
          <div class="active-users">
            <div class="active-item">
              <span class="label">今日活跃</span>
              <span class="value">{{ stats.active_users_today }}</span>
            </div>
            <div class="active-item">
              <span class="label">本周活跃</span>
              <span class="value">{{ stats.active_users_week }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>内容统计</span>
          </template>
          <div class="content-stats">
            <div class="content-item">
              <span class="label">文章总数</span>
              <span class="value">{{ stats.total_articles }}</span>
            </div>
            <div class="content-item">
              <span class="label">题目总数</span>
              <span class="value">{{ stats.total_questions }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { User, Document, Reading, Calendar } from '@element-plus/icons-vue'
import { getDashboardStats, DashboardStats } from '@/api/dashboard'

const stats = ref<DashboardStats>({
  total_users: 0,
  active_users_today: 0,
  active_users_week: 0,
  total_articles: 0,
  published_articles: 0,
  total_questions: 0,
  total_readings: 0,
  checkins_today: 0,
})

onMounted(async () => {
  stats.value = await getDashboardStats()
})
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 20px;
}

.page-title {
  margin-bottom: 24px;
  font-size: 24px;
  color: #333;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  
  &.users .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
  &.articles .stat-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
  &.readings .stat-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
  &.checkins .stat-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  
  .el-icon {
    font-size: 28px;
    color: white;
  }
}

.stat-content {
  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #333;
  }
  
  .stat-label {
    font-size: 14px;
    color: #666;
    margin-top: 4px;
  }
}

.more-stats {
  .active-users, .content-stats {
    display: flex;
    justify-content: space-around;
    padding: 20px 0;
  }
  
  .active-item, .content-item {
    text-align: center;
    
    .label {
      display: block;
      font-size: 14px;
      color: #666;
      margin-bottom: 8px;
    }
    
    .value {
      font-size: 32px;
      font-weight: 600;
      color: #409EFF;
    }
  }
}
</style>
```

### 3.7.3 文章列表 (views/articles/ArticleList.vue)

```vue
<template>
  <div class="article-list">
    <div class="page-header">
      <h2>文章管理</h2>
      <el-button type="primary" @click="$router.push('/articles/create')">
        <el-icon><Plus /></el-icon>
        创建文章
      </el-button>
    </div>
    
    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form inline>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable placeholder="全部">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索标题" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 表格 -->
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="source_book" label="来源" width="150" />
        <el-table-column prop="word_count" label="字数" width="100" />
        <el-table-column label="难度" width="100">
          <template #default="{ row }">
            <el-rate :model-value="row.article_difficulty" disabled :max="3" />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="question_count" label="题目数" width="100" />
        <el-table-column label="AI生成" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_ai_generated" type="info">AI</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/articles/${row.id}/edit`)">
              编辑
            </el-button>
            <el-button 
              v-if="row.status === 'draft'"
              size="small" 
              type="success"
              @click="handlePublish(row)"
            >
              发布
            </el-button>
            <el-button 
              size="small" 
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="loadData"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getArticleList, deleteArticle, publishArticle, Article } from '@/api/articles'

const list = ref<Article[]>([])
const loading = ref(false)

const filters = reactive({
  status: '',
  keyword: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const loadData = async () => {
  loading.value = true
  try {
    const data = await getArticleList({
      page: pagination.page,
      page_size: pagination.pageSize,
      status: filters.status || undefined,
      keyword: filters.keyword || undefined,
    })
    list.value = data.items
    pagination.total = data.total
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.status = ''
  filters.keyword = ''
  loadData()
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    draft: 'info',
    pending: 'warning',
    published: 'success',
    archived: '',
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    pending: '待审核',
    published: '已发布',
    archived: '已归档',
  }
  return map[status] || status
}

const handlePublish = async (row: Article) => {
  await ElMessageBox.confirm('确定要发布这篇文章吗？', '提示')
  await publishArticle(row.id)
  ElMessage.success('发布成功')
  loadData()
}

const handleDelete = async (row: Article) => {
  await ElMessageBox.confirm('确定要删除这篇文章吗？删除后无法恢复！', '警告', { type: 'warning' })
  await deleteArticle(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.article-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h2 {
    margin: 0;
  }
}

.filter-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
```

### 3.7.4 默认布局 (layouts/DefaultLayout.vue)

```vue
<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <span>🌟 阅读星球</span>
      </div>
      
      <el-menu
        :default-active="route.path"
        :router="true"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        
        <el-sub-menu index="content">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>内容管理</span>
          </template>
          <el-menu-item index="/articles">文章管理</el-menu-item>
          <el-menu-item index="/questions">题目管理</el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        
        <el-sub-menu index="settings">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item index="/settings/tags">标签管理</el-menu-item>
          <el-menu-item index="/settings/badges">勋章管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title">
              {{ route.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <span class="username">{{ authStore.username }}</span>
          <el-button text @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { Odometer, Document, User, Setting } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
}
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
    font-weight: 600;
    border-bottom: 1px solid #1f2d3d;
  }
  
  .el-menu {
    border-right: none;
  }
}

.header {
  background: white;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .username {
      color: #666;
    }
  }
}

.main {
  background: #f5f7fa;
  overflow-y: auto;
}
</style>
```

---

## 3.8 验收标准

### 3.8.1 功能验收

- [ ] 登录功能正常，错误提示友好
- [ ] 路由守卫正常工作
- [ ] 仪表盘数据正确显示
- [ ] 文章列表分页、筛选正常
- [ ] 文章创建、编辑、删除正常
- [ ] 文章发布、归档正常
- [ ] 题目管理功能正常
- [ ] 用户列表正常显示
- [ ] 标签、勋章管理正常

### 3.8.2 UI 验收

- [ ] 响应式布局正常
- [ ] 加载状态显示正确
- [ ] 错误提示友好
- [ ] 表单验证完整

---

## 3.9 交付物清单

| 交付物 | 文件路径 | 验收标准 |
|--------|----------|----------|
| API 封装 | `admin/src/api/` | 所有接口封装 |
| 路由配置 | `admin/src/router/` | 路由守卫正常 |
| 状态管理 | `admin/src/stores/` | 认证状态管理 |
| 登录页 | `admin/src/views/login/` | 登录功能正常 |
| 仪表盘 | `admin/src/views/dashboard/` | 数据展示正确 |
| 文章管理 | `admin/src/views/articles/` | CRUD 正常 |
| 题目管理 | `admin/src/views/questions/` | CRUD 正常 |
| 用户管理 | `admin/src/views/users/` | 列表、详情正常 |
| 系统设置 | `admin/src/views/settings/` | 标签、勋章管理 |
| 布局组件 | `admin/src/layouts/` | 侧边栏、头部正常 |
