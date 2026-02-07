import { defineStore } from 'pinia'

const THEME_KEY = 'admin_theme'
const SIDEBAR_KEY = 'admin_sidebar_collapsed'

type Theme = 'light' | 'dark'

interface AppState {
  theme: Theme
  sidebarCollapsed: boolean
  loading: boolean
  loadingMessage?: string
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    theme: (localStorage.getItem(THEME_KEY) as Theme) || 'light',
    sidebarCollapsed: localStorage.getItem(SIDEBAR_KEY) === 'true',
    loading: false,
    loadingMessage: undefined,
  }),

  getters: {
    isDarkMode: (state) => state.theme === 'dark',
  },

  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
      localStorage.setItem(SIDEBAR_KEY, String(this.sidebarCollapsed))
    },

    setSidebar(collapsed: boolean) {
      this.sidebarCollapsed = collapsed
      localStorage.setItem(SIDEBAR_KEY, String(this.sidebarCollapsed))
    },

    setTheme(theme: Theme) {
      this.theme = theme
      localStorage.setItem(THEME_KEY, theme)
      if (theme === 'dark') {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },

    toggleTheme() {
      this.setTheme(this.theme === 'light' ? 'dark' : 'light')
    },

    showLoading(message?: string) {
      this.loading = true
      this.loadingMessage = message
    },

    hideLoading() {
      this.loading = false
      this.loadingMessage = undefined
    },
  },
})
