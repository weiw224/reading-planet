import api from './index'

export interface User {
  id: number
  username: string
  nickname: string
  avatar?: string
  total_points: number
  level: number
  created_at: string
  updated_at: string
}

export interface UserListParams {
  page?: number
  page_size?: number
  keyword?: string
}

export interface UserListResponse {
  items: User[]
  total: number
  page: number
  page_size: number
}

export interface UserDetail extends User {
  email?: string
  bio?: string
  reading_stats: {
    total_articles_read: number
    total_reading_time: number
    total_questions_answered: number
    correct_rate: number
    current_streak: number
    longest_streak: number
  }
  badges: Array<{
    id: number
    name: string
    description: string
    icon: string
    earned_at: string
  }>
  recent_activities: Array<{
    id: number
    type: string
    description: string
    created_at: string
  }>
}

export const getUserList = (params: UserListParams): Promise<UserListResponse> => {
  return api.get('/admin/users/', { params })
}

export const getUser = (id: number): Promise<User> => {
  return api.get(`/admin/users/${id}`)
}

export const getUserDetail = (id: number): Promise<UserDetail> => {
  return api.get(`/admin/users/${id}/detail`)
}
