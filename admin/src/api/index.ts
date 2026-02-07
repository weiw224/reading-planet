import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const API_BASE_PATH = '/api/v1'
const REQUEST_TIMEOUT = 30000
const TOKEN_KEY = 'admin_token'
const BEARER_PREFIX = 'Bearer '
const SUCCESS_CODE = 0
const UNAUTHORIZED_CODE = 401
const DEFAULT_ERROR_MESSAGE = '请求失败'

interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

interface ErrorResponse {
  detail?: string
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL + API_BASE_PATH,
  timeout: REQUEST_TIMEOUT,
})

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (token) {
      if (!config.headers) {
        config.headers = {} as any
      }
      config.headers.Authorization = BEARER_PREFIX + token
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
    if (data.code === SUCCESS_CODE) {
      return data.data
    } else {
      ElMessage.error(data.message || DEFAULT_ERROR_MESSAGE)
      return Promise.reject(new Error(data.message))
    }
  },
  (error: AxiosError) => {
    if (error.response?.status === UNAUTHORIZED_CODE) {
      localStorage.removeItem(TOKEN_KEY)
      router?.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      const message = error.response?.data
        ? (error.response.data as ErrorResponse).detail || DEFAULT_ERROR_MESSAGE
        : '网络错误，请检查连接'
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export default api
