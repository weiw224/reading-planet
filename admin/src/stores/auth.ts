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
