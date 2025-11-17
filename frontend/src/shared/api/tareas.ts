import apiClient from './client'
import type {
  Tarea,
  CreateTareaRequest,
  UpdateTareaRequest,
  EstadisticasTareas,
  PaginatedResponse,
  TareaFilters,
  EstadoTarea,
} from '../types'

export const tareasApi = {
  getAll: async (filters?: TareaFilters): Promise<PaginatedResponse<Tarea>> => {
    const response = await apiClient.get<PaginatedResponse<Tarea>>('/tareas', {
      params: filters,
    })
    return response.data
  },

  getById: async (id: string): Promise<Tarea> => {
    const response = await apiClient.get<Tarea>(`/tareas/${id}`)
    return response.data
  },

  create: async (data: CreateTareaRequest): Promise<Tarea> => {
    const response = await apiClient.post<Tarea>('/tareas', data)
    return response.data
  },

  update: async (id: string, data: UpdateTareaRequest): Promise<Tarea> => {
    const response = await apiClient.put<Tarea>(`/tareas/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<{ mensaje: string }> => {
    const response = await apiClient.delete<{ mensaje: string }>(`/tareas/${id}`)
    return response.data
  },

  cambiarEstado: async (id: string, estado: EstadoTarea): Promise<Tarea> => {
    const response = await apiClient.patch<Tarea>(`/tareas/${id}/estado`, { estado })
    return response.data
  },

  getEstadisticas: async (): Promise<EstadisticasTareas> => {
    const response = await apiClient.get<EstadisticasTareas>('/tareas/stats')
    return response.data
  },

  getTareasHoy: async (): Promise<Tarea[]> => {
    const response = await apiClient.get<Tarea[]>('/tareas/hoy')
    return response.data
  },

  getTareasVencidas: async (): Promise<Tarea[]> => {
    const response = await apiClient.get<Tarea[]>('/tareas/vencidas')
    return response.data
  },

  getMisTareas: async (): Promise<Tarea[]> => {
    const response = await apiClient.get<Tarea[]>('/tareas/mis-tareas')
    return response.data
  },
}
