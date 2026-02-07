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

function getThemeFromStorage(): Theme {
  try {
    const stored = localStorage.getItem(THEME_KEY)
    if (stored === 'light' || stored === 'dark') {
      return stored as Theme
    }
  } catch (error) {
    console.warn('Failed to read theme from localStorage:', error)
  }
  return 'light'
}

function getSidebarFromStorage(): boolean {
  try {
    const stored = localStorage.getItem(SIDEBAR_KEY)
    return stored === 'true'
  } catch (error) {
    console.warn('Failed to read sidebar state from localStorage:', error)
    return false
  }
}

function setThemeToStorage(theme: Theme): void {
  try {
    localStorage.setItem(THEME_KEY, theme)
  } catch (error) {
    console.warn('Failed to write theme to localStorage:', error)
  }
}

function setSidebarToStorage(collapsed: boolean): void {
  try {
    localStorage.setItem(SIDEBAR_KEY, String(collapsed))
  } catch (error) {
    console.warn('Failed to write sidebar state to localStorage:', error)
  }
}

export const useAppStore = defineStore('app', {
  state: (): AppState => ({
    theme: getThemeFromStorage(),
    sidebarCollapsed: getSidebarFromStorage(),
    loading: false,
    loadingMessage: undefined,
  }),

  getters: {
    isDarkMode: (state) => state.theme === 'dark',
  },

  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
      setSidebarToStorage(this.sidebarCollapsed)
    },

    setSidebar(collapsed: boolean) {
      this.sidebarCollapsed = collapsed
      setSidebarToStorage(this.sidebarCollapsed)
    },

    setTheme(theme: Theme) {
      this.theme = theme
      setThemeToStorage(theme)
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
