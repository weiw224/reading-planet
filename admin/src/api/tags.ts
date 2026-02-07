import api from './index'

export interface Tag {
  id: number
  name: string
  category: string
  description?: string
  color?: string
  created_at: string
  updated_at: string
}

export interface TagListParams {
  page?: number
  page_size?: number
  category?: string
}

export interface TagListResponse {
  items: Tag[]
  total: number
  page: number
  page_size: number
}

export interface TagCreateParams {
  name: string
  category: string
  description?: string
  color?: string
}

export const getTagList = (params: TagListParams): Promise<TagListResponse> => {
  return api.get('/admin/tags/', { params })
}

export const getTag = (id: number): Promise<Tag> => {
  return api.get(`/admin/tags/${id}`)
}

export const createTag = (data: TagCreateParams): Promise<Tag> => {
  return api.post('/admin/tags/', data)
}

export const updateTag = (id: number, data: Partial<TagCreateParams>): Promise<Tag> => {
  return api.put(`/admin/tags/${id}`, data)
}

export const deleteTag = (id: number): Promise<void> => {
  return api.delete(`/admin/tags/${id}`)
}
