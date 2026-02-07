import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL + '/api/v1',
  timeout: 30000,
})

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
