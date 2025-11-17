// ============================================================================
// TIPOS GLOBALES - MARK-I FRONTEND
// ============================================================================

// Enums compartidos
export type Rol = 'admin' | 'gerente' | 'supervisor' | 'trabajador'
export type EstadoProyecto = 'prospecto' | 'cotizacion' | 'aprobado' | 'en_progreso' | 'pausado' | 'completado' | 'cancelado'
export type CategoriaGasto = 'materiales' | 'mano_obra' | 'transporte' | 'herramientas' | 'subcontrato' | 'permisos' | 'servicios' | 'otros'
export type EstadoTarea = 'pendiente' | 'en_progreso' | 'completada' | 'cancelada'
export type PrioridadTarea = 'baja' | 'media' | 'alta' | 'urgente'
export type MetodoCaptura = 'manual_web' | 'manual_bot' | 'foto_bot' | 'ocr_auto' | 'voz' | 'api'

// Usuario/Autenticación
export interface Usuario {
  id: string
  username: string
  email: string
  nombre_completo: string
  telefono?: string
  rol: Rol
  telegram_id?: string
  telegram_username?: string
  activo: boolean
  creado_en: string
  actualizado_en: string
  ultimo_acceso?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  usuario: Usuario
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  nombre_completo: string
  telefono?: string
  rol?: Rol
}

export interface UpdateProfileRequest {
  email?: string
  nombre_completo?: string
  telefono?: string
}

export interface ChangePasswordRequest {
  password_actual: string
  password_nueva: string
}

// Proyecto
export interface Proyecto {
  id: string
  codigo: string
  nombre: string
  cliente: string
  descripcion?: string
  presupuesto_total: string
  horas_presupuestadas?: string
  fecha_inicio?: string
  fecha_fin_estimada?: string
  fecha_fin_real?: string
  estado: EstadoProyecto
  datos_adicionales?: Record<string, unknown>
  creado_en: string
  actualizado_en: string
  dias_transcurridos?: number
  dias_restantes?: number
}

export interface CreateProyectoRequest {
  codigo: string
  nombre: string
  cliente: string
  descripcion?: string
  presupuesto_total: number | string
  horas_presupuestadas?: number | string
  fecha_inicio?: string
  fecha_fin_estimada?: string
  estado?: EstadoProyecto
}

export interface UpdateProyectoRequest extends Partial<CreateProyectoRequest> {
  fecha_fin_real?: string
}

export interface ResumenProyecto {
  id: string
  codigo: string
  nombre: string
  presupuesto_total: string
  total_gastado: string
  porcentaje_gastado: string
  balance: string
  estado: EstadoProyecto
  en_alerta: boolean
}

export interface EstadisticasProyectos {
  total_proyectos: number
  por_estado: Record<EstadoProyecto, number>
  presupuesto_total: string
  gastado_total: string
}

// Costo/Gasto
export interface Costo {
  id: string
  proyecto_id: string
  categoria: CategoriaGasto
  monto: string
  descripcion: string
  proveedor_nombre?: string
  fecha_gasto: string
  factura_url?: string
  factura_filename?: string
  metodo_captura: MetodoCaptura
  validado: boolean
  validado_por?: string
  validado_en?: string
  notas_validacion?: string
  creado_en: string
  actualizado_en: string
  dias_desde_gasto: number
  tiene_factura: boolean
  proyecto_codigo?: string
  proyecto_nombre?: string
}

export interface CreateCostoRequest {
  proyecto_id: string
  categoria: CategoriaGasto
  monto: number | string
  descripcion: string
  proveedor_nombre?: string
  fecha_gasto?: string
  metodo_captura?: MetodoCaptura
}

export interface UpdateCostoRequest extends Partial<CreateCostoRequest> {}

export interface ValidarCostoRequest {
  validado: boolean
  notas_validacion?: string
}

export interface CalcularManoObraRequest {
  proyecto_id: string
  fecha_desde: string
  fecha_hasta: string
  descripcion?: string
}

export interface CalcularManoObraResponse {
  costo_id: string
  proyecto_id: string
  proyecto_nombre: string
  periodo_inicio: string
  periodo_fin: string
  total_horas: string
  monto_total: string
  cantidad_empleados: number
  detalle_empleados: Array<{
    empleado_id: string
    empleado_nombre: string
    total_horas: string
    tarifa_hora: string
    costo_total: string
  }>
  mensaje: string
}

export interface EstadisticasCostos {
  total_costos: number
  monto_total: string
  por_categoria: Record<CategoriaGasto, string>
  promedio_por_gasto: string
  costos_validados: number
  costos_pendientes: number
}

// Tarea
export interface Tarea {
  id: string
  proyecto_id: string
  titulo: string
  descripcion?: string
  asignado_a_id?: string
  creado_por_id: string
  estado: EstadoTarea
  prioridad: PrioridadTarea
  fecha_vencimiento?: string
  fecha_inicio?: string
  fecha_completada?: string
  creado_en: string
  actualizado_en: string
  esta_vencida: boolean
  dias_hasta_vencimiento?: number
  esta_completada: boolean
  duracion_dias?: number
}

export interface CreateTareaRequest {
  proyecto_id: string
  titulo: string
  descripcion?: string
  asignado_a_id?: string
  prioridad?: PrioridadTarea
  fecha_vencimiento?: string
}

export interface UpdateTareaRequest extends Partial<CreateTareaRequest> {
  estado?: EstadoTarea
}

export interface EstadisticasTareas {
  total_tareas: number
  por_estado: Record<EstadoTarea, number>
  por_prioridad: Record<PrioridadTarea, number>
  tareas_vencidas: number
  tareas_hoy: number
}

// Empleado
export interface Empleado {
  id: string
  nombre: string
  apellido: string
  documento_identidad?: string
  telefono?: string
  email?: string
  cargo: string
  tarifa_hora: string
  fecha_ingreso?: string
  fecha_salida?: string
  activo: boolean
  notas?: string
  usuario_id?: string
  creado_en: string
  actualizado_en: string
  nombre_completo: string
  dias_antiguedad?: number
  esta_activo: boolean
}

export interface CreateEmpleadoRequest {
  nombre: string
  apellido: string
  documento_identidad?: string
  telefono?: string
  email?: string
  cargo: string
  tarifa_hora: number | string
  fecha_ingreso?: string
  activo?: boolean
  notas?: string
}

export interface UpdateEmpleadoRequest extends Partial<CreateEmpleadoRequest> {
  fecha_salida?: string
}

export interface EstadisticasEmpleados {
  total_empleados: number
  empleados_activos: number
  empleados_inactivos: number
  por_cargo: Record<string, number>
  tarifa_promedio: string
}

// Registro de Horas
export interface RegistroHora {
  id: string
  empleado_id: string
  proyecto_id: string
  tarea_id?: string
  fecha: string
  horas: string
  descripcion?: string
  creado_en: string
  actualizado_en: string
  es_hoy: boolean
  dias_desde_registro: number
  es_jornada_completa: boolean
  es_hora_extra: boolean
  horas_extras: number
}

export interface CreateRegistroHoraRequest {
  empleado_id: string
  proyecto_id: string
  tarea_id?: string
  fecha?: string
  horas: number | string
  descripcion?: string
}

export interface UpdateRegistroHoraRequest extends Partial<CreateRegistroHoraRequest> {}

export interface ResumenHorasEmpleado {
  empleado_id: string
  empleado_nombre: string
  total_horas: string
  total_horas_extras: string
  dias_trabajados: number
  tarifa_hora?: string
  costo_total?: string
}

export interface ResumenHorasProyecto {
  proyecto_id: string
  proyecto_nombre: string
  total_horas: string
  total_horas_extras: string
  cantidad_empleados: number
  costo_mano_obra?: string
}

export interface EstadisticasHoras {
  total_horas: string
  total_horas_extras: string
  total_registros: number
  promedio_horas_dia: string
}

// Notificación
export interface Notificacion {
  id: string
  usuario_id: string
  tipo: string
  titulo: string
  mensaje: string
  datos?: Record<string, unknown>
  leida: boolean
  creado_en: string
  leida_en?: string
  esta_leida: boolean
  es_reciente: boolean
  tiempo_transcurrido_str: string
}

export interface CreateNotificacionRequest {
  usuario_id: string
  tipo: string
  titulo: string
  mensaje: string
  datos?: Record<string, unknown>
}

export interface UpdateNotificacionRequest {
  leida?: boolean
}

export interface EstadisticasNotificaciones {
  total: number
  no_leidas: number
  por_tipo: Record<string, number>
}

// Paginación
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface PaginationParams {
  page?: number
  page_size?: number
}

// Filtros comunes
export interface ProyectoFilters extends PaginationParams {
  estado?: EstadoProyecto
  cliente?: string
  search?: string
}

export interface CostoFilters extends PaginationParams {
  proyecto_id?: string
  categoria?: CategoriaGasto
  fecha_desde?: string
  fecha_hasta?: string
  validado?: boolean
  con_factura?: boolean
  search?: string
}

export interface TareaFilters extends PaginationParams {
  proyecto_id?: string
  asignado_a_id?: string
  estado?: EstadoTarea
  prioridad?: PrioridadTarea
  search?: string
}

export interface EmpleadoFilters extends PaginationParams {
  cargo?: string
  activo?: boolean
  search?: string
}

export interface RegistroHoraFilters extends PaginationParams {
  empleado_id?: string
  proyecto_id?: string
  tarea_id?: string
  fecha_desde?: string
  fecha_hasta?: string
}

export interface NotificacionFilters extends PaginationParams {
  tipo?: string
  leida?: boolean
}

// Error response
export interface ApiError {
  detail: string | Array<{ msg: string; type: string }>
}
