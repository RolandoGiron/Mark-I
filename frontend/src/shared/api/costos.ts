import apiClient from './client'
import type {
  Costo,
  CreateCostoRequest,
  UpdateCostoRequest,
  ValidarCostoRequest,
  CalcularManoObraRequest,
  CalcularManoObraResponse,
  EstadisticasCostos,
  PaginatedResponse,
  CostoFilters,
} from '../types'

export const costosApi = {
  getAll: async (filters?: CostoFilters): Promise<PaginatedResponse<Costo>> => {
    const response = await apiClient.get<PaginatedResponse<Costo>>('/costos', {
      params: filters,
    })
    return response.data
  },

  getById: async (id: string): Promise<Costo> => {
    const response = await apiClient.get<Costo>(`/costos/${id}`)
    return response.data
  },

  create: async (data: CreateCostoRequest): Promise<Costo> => {
    const response = await apiClient.post<Costo>('/costos', data)
    return response.data
  },

  update: async (id: string, data: UpdateCostoRequest): Promise<Costo> => {
    const response = await apiClient.put<Costo>(`/costos/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<{ mensaje: string }> => {
    const response = await apiClient.delete<{ mensaje: string }>(`/costos/${id}`)
    return response.data
  },

  uploadFactura: async (id: string, file: File): Promise<Costo> => {
    const formData = new FormData()
    formData.append('factura', file)

    const response = await apiClient.post<Costo>(`/costos/${id}/factura`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  validar: async (id: string, data: ValidarCostoRequest): Promise<Costo> => {
    const response = await apiClient.post<Costo>(`/costos/${id}/validar`, data)
    return response.data
  },

  getTotalProyecto: async (proyectoId: string): Promise<{ total: string }> => {
    const response = await apiClient.get<{ total: string }>(`/costos/proyecto/${proyectoId}/total`)
    return response.data
  },

  getEstadisticas: async (params?: { periodo?: string }): Promise<EstadisticasCostos> => {
    const response = await apiClient.get<EstadisticasCostos>('/costos/stats/general', { params })
    return response.data
  },

  calcularManoObra: async (data: CalcularManoObraRequest): Promise<CalcularManoObraResponse> => {
    const response = await apiClient.post<CalcularManoObraResponse>('/costos/calcular-mano-obra', data)
    return response.data
  },
}
