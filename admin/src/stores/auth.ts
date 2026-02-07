import { defineStore } from 'pinia'
import { login as loginApi, LoginParams } from '@/api/auth'
import router from '@/router'

const TOKEN_KEY = 'admin_token'
const USERNAME_KEY = 'admin_username'

interface AuthState {
  token: string | null
  username: string | null
  loading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem(TOKEN_KEY),
    username: localStorage.getItem(USERNAME_KEY),
    loading: false,
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  
  actions: {
    async login(params: LoginParams) {
      try {
        this.loading = true
        const data = await loginApi(params)
        this.token = data.access_token
        this.username = params.username
        localStorage.setItem(TOKEN_KEY, data.access_token)
        localStorage.setItem(USERNAME_KEY, params.username)
        await router.push('/dashboard')
      } catch (error) {
        this.token = null
        this.username = null
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(USERNAME_KEY)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async logout() {
      this.loading = true
      try {
        this.token = null
        this.username = null
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(USERNAME_KEY)
        await router.push('/login')
      } finally {
        this.loading = false
      }
    },
  },
})
