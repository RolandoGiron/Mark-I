import apiClient from './client'
import type {
  Notificacion,
  CreateNotificacionRequest,
  UpdateNotificacionRequest,
  EstadisticasNotificaciones,
  PaginatedResponse,
  NotificacionFilters,
} from '../types'

export const notificacionesApi = {
  getAll: async (filters?: NotificacionFilters): Promise<PaginatedResponse<Notificacion>> => {
    const response = await apiClient.get<PaginatedResponse<Notificacion>>('/notificaciones', {
      params: filters,
    })
    return response.data
  },

  getById: async (id: string): Promise<Notificacion> => {
    const response = await apiClient.get<Notificacion>(`/notificaciones/${id}`)
    return response.data
  },

  create: async (data: CreateNotificacionRequest): Promise<Notificacion> => {
    const response = await apiClient.post<Notificacion>('/notificaciones', data)
    return response.data
  },

  update: async (id: string, data: UpdateNotificacionRequest): Promise<Notificacion> => {
    const response = await apiClient.patch<Notificacion>(`/notificaciones/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<{ mensaje: string }> => {
    const response = await apiClient.delete<{ mensaje: string }>(`/notificaciones/${id}`)
    return response.data
  },

  marcarLeida: async (id: string): Promise<Notificacion> => {
    const response = await apiClient.post<Notificacion>(`/notificaciones/${id}/leer`)
    return response.data
  },

  marcarTodasLeidas: async (): Promise<{ mensaje: string; actualizadas: number }> => {
    const response = await apiClient.post<{ mensaje: string; actualizadas: number }>(
      '/notificaciones/leer-todas'
    )
    return response.data
  },

  getEstadisticas: async (): Promise<EstadisticasNotificaciones> => {
    const response = await apiClient.get<EstadisticasNotificaciones>('/notificaciones/stats')
    return response.data
  },

  getRecientes: async (): Promise<Notificacion[]> => {
    const response = await apiClient.get<Notificacion[]>('/notificaciones/recientes')
    return response.data
  },
}
