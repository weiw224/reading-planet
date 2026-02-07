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
