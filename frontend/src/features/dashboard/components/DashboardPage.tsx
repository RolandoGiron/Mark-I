import { useQuery } from '@tanstack/react-query'
import { proyectosApi } from '@/shared/api/proyectos'
import { costosApi } from '@/shared/api/costos'
import { tareasApi } from '@/shared/api/tareas'
import { notificacionesApi } from '@/shared/api/notificaciones'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/ui/card'
import { Badge } from '@/shared/components/ui/badge'
import { Skeleton } from '@/shared/components/ui/skeleton'
import {
  FolderKanban,
  DollarSign,
  CheckSquare,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Bell,
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

export function DashboardPage() {
  // Queries para obtener estadísticas
  const { data: statsProyectos, isLoading: loadingProyectos } = useQuery({
    queryKey: ['estadisticas-proyectos'],
    queryFn: () => proyectosApi.getEstadisticas(),
  })

  const { data: statsCostos, isLoading: loadingCostos } = useQuery({
    queryKey: ['estadisticas-costos'],
    queryFn: () => costosApi.getEstadisticas(),
  })

  const { data: statsTareas, isLoading: loadingTareas } = useQuery({
    queryKey: ['estadisticas-tareas'],
    queryFn: () => tareasApi.getEstadisticas(),
  })

  const { data: notificaciones, isLoading: loadingNotificaciones } = useQuery({
    queryKey: ['notificaciones-recientes'],
    queryFn: () => notificacionesApi.getAll({ page_size: 5 }),
  })

  const { data: proyectosResumen, isLoading: loadingResumen } = useQuery({
    queryKey: ['proyectos-resumen'],
    queryFn: () => proyectosApi.getResumenTodos(),
  })

  // Preparar datos para gráficas
  const estadosProyectoData = statsProyectos
    ? Object.entries(statsProyectos.por_estado).map(([estado, cantidad]) => ({
        name: estado.replace('_', ' '),
        value: cantidad,
      }))
    : []

  const categoriasCostoData = statsCostos
    ? Object.entries(statsCostos.por_categoria)
        .map(([categoria, monto]) => ({
          name: categoria.replace('_', ' '),
          value: parseFloat(monto),
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 5)
    : []

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Vista general del sistema Mark-I</p>
      </div>

      {/* KPIs principales */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Proyectos Activos */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Proyectos Activos</CardTitle>
            <FolderKanban className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingProyectos ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {statsProyectos?.por_estado?.en_progreso || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  de {statsProyectos?.total_proyectos || 0} totales
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Gastos del Mes */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gastos Totales</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingCostos ? (
              <Skeleton className="h-8 w-32" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  Q{parseFloat(statsCostos?.monto_total || '0').toLocaleString('es-GT')}
                </div>
                <p className="text-xs text-muted-foreground">
                  {statsCostos?.total_costos || 0} registros
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Tareas Pendientes */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tareas Pendientes</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingTareas ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {statsTareas?.por_estado?.pendiente || 0}
                </div>
                <p className="text-xs text-destructive">
                  {statsTareas?.tareas_vencidas || 0} vencidas
                </p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Alertas */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Notificaciones</CardTitle>
            <Bell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingNotificaciones ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <>
                <div className="text-2xl font-bold">
                  {notificaciones?.items.filter((n: { leida: boolean }) => !n.leida).length || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  sin leer
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Gráficas */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Estados de Proyectos */}
        <Card>
          <CardHeader>
            <CardTitle>Proyectos por Estado</CardTitle>
          </CardHeader>
          <CardContent>
            {loadingProyectos ? (
              <Skeleton className="h-64 w-full" />
            ) : estadosProyectoData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={estadosProyectoData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {estadosProyectoData.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-muted-foreground py-20">No hay datos disponibles</p>
            )}
          </CardContent>
        </Card>

        {/* Gastos por Categoría */}
        <Card>
          <CardHeader>
            <CardTitle>Top 5 Categorías de Gasto</CardTitle>
          </CardHeader>
          <CardContent>
            {loadingCostos ? (
              <Skeleton className="h-64 w-full" />
            ) : categoriasCostoData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={categoriasCostoData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip formatter={(value) => `Q${parseFloat(String(value)).toLocaleString('es-GT')}`} />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-center text-muted-foreground py-20">No hay datos disponibles</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Proyectos en Alerta */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-500" />
            Proyectos que Requieren Atención
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loadingResumen ? (
            <div className="space-y-2">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </div>
          ) : proyectosResumen && proyectosResumen.length > 0 ? (
            <div className="space-y-3">
              {proyectosResumen
                .filter((p: { en_alerta: boolean }) => p.en_alerta)
                .slice(0, 5)
                .map((proyecto: { id: string; codigo: string; nombre: string; presupuesto_total: string; total_gastado: string; porcentaje_gastado: string; balance: string }) => {
                  const porcentaje = parseFloat(proyecto.porcentaje_gastado)
                  const balance = parseFloat(proyecto.balance)
                  const isOverBudget = balance < 0

                  return (
                    <div
                      key={proyecto.id}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{proyecto.nombre}</h4>
                          <Badge variant="outline" className="text-xs">
                            {proyecto.codigo}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                          <span>
                            Presupuesto: Q{parseFloat(proyecto.presupuesto_total).toLocaleString('es-GT')}
                          </span>
                          <span>
                            Gastado: Q{parseFloat(proyecto.total_gastado).toLocaleString('es-GT')}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <div className="flex items-center gap-1 text-sm font-medium">
                            {isOverBudget ? (
                              <>
                                <TrendingDown className="h-4 w-4 text-destructive" />
                                <span className="text-destructive">{porcentaje.toFixed(1)}%</span>
                              </>
                            ) : (
                              <>
                                <TrendingUp className="h-4 w-4 text-green-600" />
                                <span className={porcentaje > 80 ? 'text-yellow-600' : 'text-green-600'}>
                                  {porcentaje.toFixed(1)}%
                                </span>
                              </>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Balance: Q{Math.abs(balance).toLocaleString('es-GT')}
                          </p>
                        </div>
                        <Badge variant={isOverBudget ? 'destructive' : 'warning'}>
                          {isOverBudget ? 'Sobrepresupuesto' : 'Alerta'}
                        </Badge>
                      </div>
                    </div>
                  )
                })}
              {proyectosResumen.filter((p: { en_alerta: boolean }) => p.en_alerta).length === 0 && (
                <p className="text-center text-muted-foreground py-8">
                  No hay proyectos en alerta
                </p>
              )}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No hay proyectos registrados</p>
          )}
        </CardContent>
      </Card>

      {/* Notificaciones Recientes */}
      <Card>
        <CardHeader>
          <CardTitle>Notificaciones Recientes</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingNotificaciones ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : notificaciones && notificaciones.items.length > 0 ? (
            <div className="space-y-2">
              {notificaciones.items.map((notif: { id: string; leida: boolean; titulo: string; mensaje: string; tiempo_transcurrido_str: string }) => (
                <div
                  key={notif.id}
                  className={`flex items-start gap-3 p-3 border rounded-lg ${
                    !notif.leida ? 'bg-accent/50' : ''
                  }`}
                >
                  <Bell className={`h-4 w-4 mt-0.5 ${!notif.leida ? 'text-primary' : 'text-muted-foreground'}`} />
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium">{notif.titulo}</p>
                    <p className="text-xs text-muted-foreground">{notif.mensaje}</p>
                    <p className="text-xs text-muted-foreground">{notif.tiempo_transcurrido_str}</p>
                  </div>
                  {!notif.leida && <Badge variant="default" className="text-xs">Nueva</Badge>}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No hay notificaciones</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
