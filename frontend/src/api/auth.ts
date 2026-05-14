import http from './http'

export interface AuthResponse {
  token: string
  username: string
  userId: number
}

export interface UserProfile {
  id: number
  username: string
  email: string | null
  createdAt: string
}

export const authApi = {
  register: (username: string, password: string, email?: string) =>
    http.post<AuthResponse>('/auth/register', { username, password, email }),

  login: (username: string, password: string) =>
    http.post<AuthResponse>('/auth/login', { username, password }),

  getProfile: () =>
    http.get<UserProfile>('/auth/profile'),

  updateProfile: (data: { email: string }) =>
    http.put<UserProfile>('/auth/profile', data),

  changePassword: (currentPassword: string, newPassword: string) =>
    http.put('/auth/password', { currentPassword, newPassword }),
}
