import apiClient from './client'
import type {
  RegistroHora,
  CreateRegistroHoraRequest,
  UpdateRegistroHoraRequest,
  ResumenHorasEmpleado,
  ResumenHorasProyecto,
  EstadisticasHoras,
  PaginatedResponse,
  RegistroHoraFilters,
} from '../types'

export const horasApi = {
  getAll: async (filters?: RegistroHoraFilters): Promise<PaginatedResponse<RegistroHora>> => {
    const response = await apiClient.get<PaginatedResponse<RegistroHora>>('/horas', {
      params: filters,
    })
    return response.data
  },

  getById: async (id: string): Promise<RegistroHora> => {
    const response = await apiClient.get<RegistroHora>(`/horas/${id}`)
    return response.data
  },

  create: async (data: CreateRegistroHoraRequest): Promise<RegistroHora> => {
    const response = await apiClient.post<RegistroHora>('/horas', data)
    return response.data
  },

  update: async (id: string, data: UpdateRegistroHoraRequest): Promise<RegistroHora> => {
    const response = await apiClient.put<RegistroHora>(`/horas/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<{ mensaje: string }> => {
    const response = await apiClient.delete<{ mensaje: string }>(`/horas/${id}`)
    return response.data
  },

  getEstadisticas: async (params?: RegistroHoraFilters): Promise<EstadisticasHoras> => {
    const response = await apiClient.get<EstadisticasHoras>('/horas/stats', { params })
    return response.data
  },

  getResumenEmpleados: async (params?: RegistroHoraFilters): Promise<ResumenHorasEmpleado[]> => {
    const response = await apiClient.get<ResumenHorasEmpleado[]>('/horas/resumen/empleados', {
      params,
    })
    return response.data
  },

  getResumenProyectos: async (params?: RegistroHoraFilters): Promise<ResumenHorasProyecto[]> => {
    const response = await apiClient.get<ResumenHorasProyecto[]>('/horas/resumen/proyectos', {
      params,
    })
    return response.data
  },

  getTotalEmpleado: async (empleadoId: string, params?: RegistroHoraFilters): Promise<{ total_horas: string }> => {
    const response = await apiClient.get<{ total_horas: string }>(`/horas/empleado/${empleadoId}/total`, {
      params,
    })
    return response.data
  },

  getTotalProyecto: async (proyectoId: string, params?: RegistroHoraFilters): Promise<{ total_horas: string }> => {
    const response = await apiClient.get<{ total_horas: string }>(`/horas/proyecto/${proyectoId}/total`, {
      params,
    })
    return response.data
  },
}
