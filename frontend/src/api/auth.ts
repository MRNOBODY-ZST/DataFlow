import http from './http'

export interface AuthResponse {
  token: string
  username: string
  userId: number
}

export const authApi = {
  register: (username: string, password: string, email?: string) =>
    http.post<AuthResponse>('/auth/register', { username, password, email }),

  login: (username: string, password: string) =>
    http.post<AuthResponse>('/auth/login', { username, password }),
}
