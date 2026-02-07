import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'

export function useAuth() {
  const authStore = useAuthStore()

  const isLoggedIn = computed(() => authStore.isLoggedIn)
  
  const getUser = computed(() => ({
    username: authStore.username,
  }))

  const logout = () => {
    authStore.logout()
  }

  return {
    isLoggedIn,
    getUser,
    logout,
  }
}
