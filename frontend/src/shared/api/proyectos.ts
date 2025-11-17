import apiClient from './client'
import type {
  Proyecto,
  CreateProyectoRequest,
  UpdateProyectoRequest,
  ResumenProyecto,
  EstadisticasProyectos,
  PaginatedResponse,
  ProyectoFilters,
} from '../types'

export const proyectosApi = {
  getAll: async (filters?: ProyectoFilters): Promise<PaginatedResponse<Proyecto>> => {
    const response = await apiClient.get<PaginatedResponse<Proyecto>>('/proyectos', {
      params: filters,
    })
    return response.data
  },

  getById: async (id: string): Promise<Proyecto> => {
    const response = await apiClient.get<Proyecto>(`/proyectos/${id}`)
    return response.data
  },

  getByCodigo: async (codigo: string): Promise<Proyecto> => {
    const response = await apiClient.get<Proyecto>(`/proyectos/codigo/${codigo}`)
    return response.data
  },

  create: async (data: CreateProyectoRequest): Promise<Proyecto> => {
    const response = await apiClient.post<Proyecto>('/proyectos', data)
    return response.data
  },

  update: async (id: string, data: UpdateProyectoRequest): Promise<Proyecto> => {
    const response = await apiClient.put<Proyecto>(`/proyectos/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<{ mensaje: string }> => {
    const response = await apiClient.delete<{ mensaje: string }>(`/proyectos/${id}`)
    return response.data
  },

  getResumen: async (id: string): Promise<ResumenProyecto> => {
    const response = await apiClient.get<ResumenProyecto>(`/proyectos/${id}/resumen`)
    return response.data
  },

  getEstadisticas: async (): Promise<EstadisticasProyectos> => {
    const response = await apiClient.get<EstadisticasProyectos>('/proyectos/stats/general')
    return response.data
  },

  getResumenTodos: async (): Promise<ResumenProyecto[]> => {
    const response = await apiClient.get<ResumenProyecto[]>('/proyectos/resumen/todos')
    return response.data
  },
}
