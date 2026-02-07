import api from './index'

export interface Question {
  id: number
  content: string
  article_id: number
  options: string[]
  correct_answer: number
  type: string
  created_at: string
  updated_at: string
}

export interface QuestionListParams {
  page?: number
  page_size?: number
  article_id?: number
  question_type?: string
}

export interface QuestionListResponse {
  items: Question[]
  total: number
  page: number
  page_size: number
}

export interface QuestionCreateParams {
  content: string
  article_id: number
  options: string[]
  correct_answer: number
  type: string
}

export const getQuestionList = (params: QuestionListParams): Promise<QuestionListResponse> => {
  return api.get('/admin/questions/', { params })
}

export const getQuestion = (id: number): Promise<Question> => {
  return api.get(`/admin/questions/${id}`)
}

export const createQuestion = (data: QuestionCreateParams): Promise<Question> => {
  return api.post('/admin/questions/', data)
}

export const updateQuestion = (id: number, data: Partial<QuestionCreateParams>): Promise<Question> => {
  return api.put(`/admin/questions/${id}`, data)
}

export const deleteQuestion = (id: number): Promise<void> => {
  return api.delete(`/admin/questions/${id}`)
}
