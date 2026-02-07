import api from './index'

export interface Article {
  id: number
  title: string
  content: string
  source_book?: string
  source_chapter?: string
  is_excerpt: boolean
  word_count: number
  reading_time: number
  article_difficulty: number
  status: string
  is_ai_generated: boolean
  created_at: string
  updated_at: string
  tags: Array<{ id: number; name: string; category: string }>
  question_count: number
}

export interface ArticleListParams {
  page?: number
  page_size?: number
  status?: string
  keyword?: string
}

export interface ArticleListResponse {
  items: Article[]
  total: number
  page: number
  page_size: number
}

export interface ArticleCreateParams {
  title: string
  content: string
  source_book?: string
  source_chapter?: string
  is_excerpt?: boolean
  article_difficulty: number
  tag_ids: number[]
}

export const getArticleList = (params: ArticleListParams): Promise<ArticleListResponse> => {
  return api.get('/admin/articles/', { params })
}

export const getArticle = (id: number): Promise<Article> => {
  return api.get(`/admin/articles/${id}`)
}

export const createArticle = (data: ArticleCreateParams): Promise<Article> => {
  return api.post('/admin/articles/', data)
}

export const updateArticle = (id: number, data: Partial<ArticleCreateParams>): Promise<Article> => {
  return api.put(`/admin/articles/${id}`, data)
}

export const deleteArticle = (id: number): Promise<void> => {
  return api.delete(`/admin/articles/${id}`)
}

export const publishArticle = (id: number): Promise<void> => {
  return api.post(`/admin/articles/${id}/publish`)
}

export const archiveArticle = (id: number): Promise<void> => {
  return api.post(`/admin/articles/${id}/archive`)
}
