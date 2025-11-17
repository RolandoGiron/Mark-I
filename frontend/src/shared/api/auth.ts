import apiClient from './client'
import type {
  Usuario,
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  UpdateProfileRequest,
  ChangePasswordRequest,
  PaginatedResponse,
  PaginationParams,
} from '../types'

export const authApi = {
  // Autenticación
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  register: async (data: RegisterRequest): Promise<Usuario> => {
    const response = await apiClient.post<Usuario>('/auth/register', data)
    return response.data
  },

  // Perfil
  getMe: async (): Promise<Usuario> => {
    const response = await apiClient.get<Usuario>('/auth/me')
    return response.data
  },

  updateMe: async (data: UpdateProfileRequest): Promise<Usuario> => {
    const response = await apiClient.put<Usuario>('/auth/me', data)
    return response.data
  },

  changePassword: async (data: ChangePasswordRequest): Promise<{ mensaje: string }> => {
    const response = await apiClient.post<{ mensaje: string }>('/auth/me/change-password', data)
    return response.data
  },

  // Administración de usuarios (ADMIN only)
  getUsuarios: async (params?: PaginationParams): Promise<PaginatedResponse<Usuario>> => {
    const response = await apiClient.get<PaginatedResponse<Usuario>>('/auth/usuarios', { params })
    return response.data
  },

  getUsuario: async (id: string): Promise<Usuario> => {
    const response = await apiClient.get<Usuario>(`/auth/usuarios/${id}`)
    return response.data
  },

  updateUsuario: async (id: string, data: Partial<Usuario>): Promise<Usuario> => {
    const response = await apiClient.put<Usuario>(`/auth/usuarios/${id}`, data)
    return response.data
  },

  deleteUsuario: async (id: string): Promise<{ mensaje: string }> => {
    const response = await apiClient.delete<{ mensaje: string }>(`/auth/usuarios/${id}`)
    return response.data
  },
}
