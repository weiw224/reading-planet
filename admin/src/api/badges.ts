import api from './index'

export interface Badge {
  id: number
  name: string
  description?: string
  icon: string
  color?: string
  created_at: string
  updated_at: string
}

export interface BadgeListParams {
  page?: number
  page_size?: number
}

export interface BadgeListResponse {
  items: Badge[]
  total: number
  page: number
  page_size: number
}

export interface BadgeCreateParams {
  name: string
  description?: string
  icon: string
  color?: string
}

export const getBadgeList = (params: BadgeListParams): Promise<BadgeListResponse> => {
  return api.get('/admin/badges/', { params })
}

export const getBadge = (id: number): Promise<Badge> => {
  return api.get(`/admin/badges/${id}`)
}

export const createBadge = (data: BadgeCreateParams): Promise<Badge> => {
  return api.post('/admin/badges/', data)
}

export const updateBadge = (id: number, data: Partial<BadgeCreateParams>): Promise<Badge> => {
  return api.put(`/admin/badges/${id}`, data)
}

export const deleteBadge = (id: number): Promise<void> => {
  return api.delete(`/admin/badges/${id}`)
}
