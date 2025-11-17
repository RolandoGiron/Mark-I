import apiClient from './client'
import type {
  Empleado,
  CreateEmpleadoRequest,
  UpdateEmpleadoRequest,
  EstadisticasEmpleados,
  PaginatedResponse,
  EmpleadoFilters,
} from '../types'

export const personalApi = {
  getAll: async (filters?: EmpleadoFilters): Promise<PaginatedResponse<Empleado>> => {
    const response = await apiClient.get<PaginatedResponse<Empleado>>('/personal', {
      params: filters,
    })
    return response.data
  },

  getById: async (id: string): Promise<Empleado> => {
    const response = await apiClient.get<Empleado>(`/personal/${id}`)
    return response.data
  },

  getByDocumento: async (documento: string): Promise<Empleado> => {
    const response = await apiClient.get<Empleado>(`/personal/documento/${documento}`)
    return response.data
  },

  create: async (data: CreateEmpleadoRequest): Promise<Empleado> => {
    const response = await apiClient.post<Empleado>('/personal', data)
    return response.data
  },

  update: async (id: string, data: UpdateEmpleadoRequest): Promise<Empleado> => {
    const response = await apiClient.put<Empleado>(`/personal/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<{ mensaje: string }> => {
    const response = await apiClient.delete<{ mensaje: string }>(`/personal/${id}`)
    return response.data
  },

  getEstadisticas: async (): Promise<EstadisticasEmpleados> => {
    const response = await apiClient.get<EstadisticasEmpleados>('/personal/stats')
    return response.data
  },
}
