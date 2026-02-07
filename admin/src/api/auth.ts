import api from './index'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  expires_in: number
}

export const login = (params: LoginParams): Promise<LoginResponse> => {
  return api.post('/auth/admin-login', params)
}
