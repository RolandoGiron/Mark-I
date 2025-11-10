"""
Script para poblar la base de datos con datos de prueba.
Útil para desarrollo y testing.
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path para poder importar app
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from decimal import Decimal

from app.database import SessionLocal, init_db
from app.modules.auth.models import Usuario, RolUsuario
from app.modules.auth.utils import hash_password
from app.modules.proyectos.models import Proyecto, EstadoProyecto
from app.modules.costos.models import Costo, CategoriaGasto, MetodoCaptura
from app.modules.personal.models import Empleado
from app.modules.tareas.models import Tarea
from app.modules.horas.models import RegistroHora
from app.modules.notificaciones.models import Notificacion


def crear_usuarios(db):
    """Crea usuarios de prueba"""
    usuarios = [
        {
            "username": "admin",
            "email": "admin@marki.com",
            "nombre_completo": "Administrador del Sistema",
            "hashed_password": hash_password("admin123"),
            "rol": RolUsuario.ADMIN,
            "telefono": "+52 55 1234 5678"
        },
        {
            "username": "jmartinez",
            "email": "juan.martinez@marki.com",
            "nombre_completo": "Juan Martinez",
            "hashed_password": hash_password("gerente123"),
            "rol": RolUsuario.GERENTE,
            "telefono": "+52 55 2345 6789"
        },
        {
            "username": "mgarcia",
            "email": "maria.garcia@marki.com",
            "nombre_completo": "María García",
            "hashed_password": hash_password("supervisor123"),
            "rol": RolUsuario.SUPERVISOR,
            "telefono": "+52 55 3456 7890"
        },
        {
            "username": "plopez",
            "email": "pedro.lopez@marki.com",
            "nombre_completo": "Pedro López",
            "hashed_password": hash_password("trabajador123"),
            "rol": RolUsuario.TRABAJADOR,
            "telefono": "+52 55 4567 8901"
        }
    ]

    usuarios_creados = []
    for usuario_data in usuarios:
        usuario = Usuario(**usuario_data)
        db.add(usuario)
        usuarios_creados.append(usuario)

    db.commit()
    print(f"✅ {len(usuarios_creados)} usuarios creados")
    return usuarios_creados


def crear_proyectos(db):
    """Crea proyectos de prueba"""
    proyectos = [
        {
            "codigo": "CASA-001",
            "nombre": "Casa Martinez #23",
            "cliente": "Juan Martinez",
            "descripcion": "Construcción de casa residencial de 2 pisos en zona norte",
            "presupuesto_total": Decimal("500000.00"),
            "horas_presupuestadas": Decimal("200.0"),
            "fecha_inicio": datetime.utcnow() - timedelta(days=30),
            "fecha_fin_estimada": datetime.utcnow() + timedelta(days=90),
            "estado": EstadoProyecto.EN_PROGRESO,
            "metadata": {"ubicacion": "Zona Norte", "tipo": "Residencial", "pisos": 2}
        },
        {
            "codigo": "LOCAL-002",
            "nombre": "Local Comercial Centro",
            "cliente": "Comercializadora ABC S.A.",
            "descripcion": "Remodelación de local comercial en centro histórico",
            "presupuesto_total": Decimal("350000.00"),
            "horas_presupuestadas": Decimal("150.0"),
            "fecha_inicio": datetime.utcnow() - timedelta(days=15),
            "fecha_fin_estimada": datetime.utcnow() + timedelta(days=60),
            "estado": EstadoProyecto.EN_PROGRESO,
            "metadata": {"ubicacion": "Centro", "tipo": "Comercial", "metros": 120}
        },
        {
            "codigo": "OFIC-003",
            "nombre": "Oficinas Corporativas Norte",
            "cliente": "Tech Solutions Corp",
            "descripcion": "Construcción de oficinas corporativas con espacios modernos",
            "presupuesto_total": Decimal("1200000.00"),
            "horas_presupuestadas": Decimal("400.0"),
            "fecha_inicio": None,
            "fecha_fin_estimada": None,
            "estado": EstadoProyecto.APROBADO,
            "metadata": {"ubicacion": "Parque Industrial Norte", "tipo": "Corporativo", "pisos": 3}
        },
        {
            "codigo": "DEPA-004",
            "nombre": "Departamentos Residencial Sur",
            "cliente": "Inmobiliaria Del Sur",
            "descripcion": "Complejo de 8 departamentos residenciales",
            "presupuesto_total": Decimal("2500000.00"),
            "horas_presupuestadas": Decimal("800.0"),
            "fecha_inicio": None,
            "fecha_fin_estimada": None,
            "estado": EstadoProyecto.COTIZACION,
            "metadata": {"ubicacion": "Zona Sur", "tipo": "Residencial", "unidades": 8}
        },
    ]

    proyectos_creados = []
    for proyecto_data in proyectos:
        proyecto = Proyecto(**proyecto_data)
        db.add(proyecto)
        proyectos_creados.append(proyecto)

    db.commit()
    print(f"✅ {len(proyectos_creados)} proyectos creados")
    return proyectos_creados


def crear_costos(db, proyectos):
    """Crea costos/gastos de prueba"""
    # Solo agregar costos a proyectos en progreso
    proyectos_activos = [p for p in proyectos if p.estado == EstadoProyecto.EN_PROGRESO]

    costos = []

    # Casa Martinez
    casa_martinez = next(p for p in proyectos_activos if p.codigo == "CASA-001")
    costos_casa = [
        {
            "proyecto_id": casa_martinez.id,
            "categoria": CategoriaGasto.MATERIALES,
            "monto": Decimal("45000.00"),
            "descripcion": "Cemento, arena y grava para cimientos",
            "proveedor_nombre": "Home Depot",
            "fecha_gasto": datetime.utcnow() - timedelta(days=25),
            "metodo_captura": MetodoCaptura.MANUAL_WEB,
            "validado": True
        },
        {
            "proyecto_id": casa_martinez.id,
            "categoria": CategoriaGasto.MATERIALES,
            "monto": Decimal("32500.00"),
            "descripcion": "Varilla y alambrón para estructura",
            "proveedor_nombre": "Aceros del Norte",
            "fecha_gasto": datetime.utcnow() - timedelta(days=20),
            "metodo_captura": MetodoCaptura.FOTO_BOT,
            "validado": True
        },
        {
            "proyecto_id": casa_martinez.id,
            "categoria": CategoriaGasto.MANO_OBRA,
            "monto": Decimal("28000.00"),
            "descripcion": "Pago de albañiles semana 1-2",
            "proveedor_nombre": None,
            "fecha_gasto": datetime.utcnow() - timedelta(days=18),
            "metodo_captura": MetodoCaptura.MANUAL_WEB,
            "validado": True
        },
        {
            "proyecto_id": casa_martinez.id,
            "categoria": CategoriaGasto.HERRAMIENTAS,
            "monto": Decimal("8500.00"),
            "descripcion": "Renta de revolvedora y andamios",
            "proveedor_nombre": "Rentas y Andamios SA",
            "fecha_gasto": datetime.utcnow() - timedelta(days=15),
            "metodo_captura": MetodoCaptura.MANUAL_WEB,
            "validado": True
        },
        {
            "proyecto_id": casa_martinez.id,
            "categoria": CategoriaGasto.MATERIALES,
            "monto": Decimal("15200.00"),
            "descripcion": "Block y ladrillos para muros",
            "proveedor_nombre": "Materiales García",
            "fecha_gasto": datetime.utcnow() - timedelta(days=10),
            "metodo_captura": MetodoCaptura.MANUAL_WEB,
            "validado": False
        },
    ]

    # Local Comercial
    local = next(p for p in proyectos_activos if p.codigo == "LOCAL-002")
    costos_local = [
        {
            "proyecto_id": local.id,
            "categoria": CategoriaGasto.MATERIALES,
            "monto": Decimal("22000.00"),
            "descripcion": "Cancelería de aluminio para fachada",
            "proveedor_nombre": "Aluminios Modernos",
            "fecha_gasto": datetime.utcnow() - timedelta(days=12),
            "metodo_captura": MetodoCaptura.MANUAL_WEB,
            "validado": True
        },
        {
            "proyecto_id": local.id,
            "categoria": CategoriaGasto.PERMISOS,
            "monto": Decimal("5500.00"),
            "descripcion": "Permiso de remodelación centro histórico",
            "proveedor_nombre": "Municipio",
            "fecha_gasto": datetime.utcnow() - timedelta(days=14),
            "metodo_captura": MetodoCaptura.MANUAL_WEB,
            "validado": True
        },
        {
            "proyecto_id": local.id,
            "categoria": CategoriaGasto.SUBCONTRATO,
            "monto": Decimal("18000.00"),
            "descripcion": "Instalación eléctrica especializada",
            "proveedor_nombre": "Eléctricos Pro SA",
            "fecha_gasto": datetime.utcnow() - timedelta(days=8),
            "metodo_captura": MetodoCaptura.MANUAL_WEB,
            "validado": False
        },
    ]

    costos.extend(costos_casa)
    costos.extend(costos_local)

    costos_creados = []
    for costo_data in costos:
        costo = Costo(**costo_data)
        db.add(costo)
        costos_creados.append(costo)

    db.commit()
    print(f"✅ {len(costos_creados)} costos/gastos creados")
    return costos_creados


def crear_empleados(db, usuarios):
    """Crea empleados de prueba"""
    empleados_data = [
        {
            "nombre": "Carlos",
            "apellido": "Hernández",
            "documento_identidad": "RFC-CH-001",
            "telefono": "+52 55 5678 9012",
            "email": "carlos.h@example.com",
            "cargo": "maestro_obra",
            "tarifa_hora": Decimal("1800.00"),
            "fecha_ingreso": datetime.utcnow() - timedelta(days=180),
            "activo": True,
            "usuario_id": None,  # Sin usuario asociado
            "notas": "Maestro de obra con 15 años de experiencia"
        },
        {
            "nombre": "Roberto",
            "apellido": "Sánchez",
            "documento_identidad": "RFC-RS-002",
            "telefono": "+52 55 6789 0123",
            "cargo": "oficial",
            "tarifa_hora": Decimal("1500.00"),
            "fecha_ingreso": datetime.utcnow() - timedelta(days=90),
            "activo": True,
            "usuario_id": usuarios[3].id if len(usuarios) > 3 else None,  # Pedro López
            "notas": "Oficial especializado en acabados"
        },
        {
            "nombre": "Miguel",
            "apellido": "Torres",
            "documento_identidad": "RFC-MT-003",
            "cargo": "obrero",
            "tarifa_hora": Decimal("1200.00"),
            "fecha_ingreso": datetime.utcnow() - timedelta(days=45),
            "activo": True,
            "notas": "Obrero general"
        },
        {
            "nombre": "Luis",
            "apellido": "Ramírez",
            "cargo": "obrero",
            "tarifa_hora": Decimal("1200.00"),
            "fecha_ingreso": datetime.utcnow() - timedelta(days=30),
            "activo": True
        },
        {
            "nombre": "Ana",
            "apellido": "Morales",
            "documento_identidad": "RFC-AM-005",
            "cargo": "ingeniero",
            "tarifa_hora": Decimal("2500.00"),
            "fecha_ingreso": datetime.utcnow() - timedelta(days=365),
            "activo": True,
            "usuario_id": usuarios[2].id if len(usuarios) > 2 else None,  # María García
            "notas": "Ingeniera civil supervisora"
        },
    ]

    empleados = []
    for emp_data in empleados_data:
        empleado = Empleado(**emp_data)
        db.add(empleado)
        empleados.append(empleado)

    db.commit()
    print(f"✅ {len(empleados)} empleados creados")
    return empleados


def crear_tareas(db, proyectos, usuarios):
    """Crea tareas de prueba"""
    casa_martinez = next((p for p in proyectos if p.codigo == "CASA-001"), None)
    local = next((p for p in proyectos if p.codigo == "LOCAL-002"), None)

    tareas_data = [
        # Tareas Casa Martinez
        {
            "proyecto_id": casa_martinez.id if casa_martinez else proyectos[0].id,
            "titulo": "Excavación para cimientos",
            "descripcion": "Realizar excavación de 2m de profundidad para cimientos",
            "asignado_a_id": usuarios[2].id,  # María García
            "creado_por_id": usuarios[1].id,  # Juan Martinez
            "estado": "completada",
            "prioridad": "alta",
            "fecha_inicio": datetime.utcnow() - timedelta(days=28),
            "fecha_vencimiento": datetime.utcnow() - timedelta(days=25),
            "fecha_completada": datetime.utcnow() - timedelta(days=26)
        },
        {
            "proyecto_id": casa_martinez.id if casa_martinez else proyectos[0].id,
            "titulo": "Armado de estructura de acero",
            "descripcion": "Armar estructura metálica según planos",
            "asignado_a_id": usuarios[3].id,  # Pedro López
            "creado_por_id": usuarios[1].id,
            "estado": "en_progreso",
            "prioridad": "alta",
            "fecha_inicio": datetime.utcnow() - timedelta(days=15),
            "fecha_vencimiento": datetime.utcnow() + timedelta(days=5)
        },
        {
            "proyecto_id": casa_martinez.id if casa_martinez else proyectos[0].id,
            "titulo": "Instalación eléctrica planta baja",
            "descripcion": "Instalación completa de cableado eléctrico",
            "asignado_a_id": usuarios[2].id,
            "creado_por_id": usuarios[1].id,
            "estado": "pendiente",
            "prioridad": "media",
            "fecha_vencimiento": datetime.utcnow() + timedelta(days=15)
        },
        {
            "proyecto_id": casa_martinez.id if casa_martinez else proyectos[0].id,
            "titulo": "Revisión de planos arquitectónicos",
            "descripcion": "Revisar y aprobar modificaciones a planos",
            "asignado_a_id": usuarios[1].id,
            "creado_por_id": usuarios[0].id,
            "estado": "pendiente",
            "prioridad": "urgente",
            "fecha_vencimiento": datetime.utcnow()  # Vence hoy
        },
        # Tareas Local Comercial
        {
            "proyecto_id": local.id if local else proyectos[1].id,
            "titulo": "Demolición de muros interiores",
            "descripcion": "Demoler muros no estructurales según plano de remodelación",
            "asignado_a_id": usuarios[3].id,
            "creado_por_id": usuarios[1].id,
            "estado": "completada",
            "prioridad": "alta",
            "fecha_inicio": datetime.utcnow() - timedelta(days=14),
            "fecha_vencimiento": datetime.utcnow() - timedelta(days=10),
            "fecha_completada": datetime.utcnow() - timedelta(days=11)
        },
        {
            "proyecto_id": local.id if local else proyectos[1].id,
            "titulo": "Instalación de cancelería",
            "descripcion": "Instalar cancelería de aluminio en fachada",
            "asignado_a_id": usuarios[2].id,
            "creado_por_id": usuarios[1].id,
            "estado": "en_progreso",
            "prioridad": "alta",
            "fecha_inicio": datetime.utcnow() - timedelta(days=5),
            "fecha_vencimiento": datetime.utcnow() + timedelta(days=3)
        },
    ]

    tareas = []
    for tarea_data in tareas_data:
        tarea = Tarea(**tarea_data)
        db.add(tarea)
        tareas.append(tarea)

    db.commit()
    print(f"✅ {len(tareas)} tareas creadas")
    return tareas


def crear_registros_horas(db, empleados, proyectos, tareas):
    """Crea registros de horas de prueba"""
    if not empleados or not proyectos:
        print("⚠️  No hay empleados o proyectos para crear registros de horas")
        return []

    casa_martinez = next((p for p in proyectos if p.codigo == "CASA-001"), proyectos[0])
    local = next((p for p in proyectos if p.codigo == "LOCAL-002"), proyectos[1] if len(proyectos) > 1 else proyectos[0])

    registros_data = []

    # Registros para empleado 1 (últimos 10 días)
    for dia in range(10):
        registros_data.append({
            "empleado_id": empleados[0].id,
            "proyecto_id": casa_martinez.id,
            "tarea_id": tareas[0].id if tareas else None,
            "fecha": (datetime.utcnow() - timedelta(days=dia)).date(),
            "horas": Decimal("8.0") if dia % 3 != 0 else Decimal("9.0"),
            "descripcion": f"Trabajo en cimientos - día {10-dia}"
        })

    # Registros para empleado 2
    for dia in range(8):
        registros_data.append({
            "empleado_id": empleados[1].id if len(empleados) > 1 else empleados[0].id,
            "proyecto_id": casa_martinez.id,
            "tarea_id": tareas[1].id if len(tareas) > 1 else None,
            "fecha": (datetime.utcnow() - timedelta(days=dia)).date(),
            "horas": Decimal("8.0"),
            "descripcion": f"Armado de estructura - día {8-dia}"
        })

    # Registros para empleado 3 en local comercial
    for dia in range(5):
        registros_data.append({
            "empleado_id": empleados[2].id if len(empleados) > 2 else empleados[0].id,
            "proyecto_id": local.id,
            "tarea_id": tareas[4].id if len(tareas) > 4 else None,
            "fecha": (datetime.utcnow() - timedelta(days=dia)).date(),
            "horas": Decimal("7.5"),
            "descripcion": f"Demolición - día {5-dia}"
        })

    registros = []
    for reg_data in registros_data:
        registro = RegistroHora(**reg_data)
        db.add(registro)
        registros.append(registro)

    db.commit()
    print(f"✅ {len(registros)} registros de horas creados")
    return registros


def crear_notificaciones(db, usuarios, tareas):
    """Crea notificaciones de prueba"""
    notificaciones_data = [
        {
            "usuario_id": usuarios[2].id,  # María García
            "tipo": "tarea_asignada",
            "titulo": "Nueva tarea asignada",
            "mensaje": "Te han asignado la tarea 'Excavación para cimientos'",
            "leida": True,
            "datos": {"tarea_id": tareas[0].id if tareas else None},
            "creado_en": datetime.utcnow() - timedelta(days=28)
        },
        {
            "usuario_id": usuarios[3].id,  # Pedro López
            "tipo": "tarea_asignada",
            "titulo": "Nueva tarea asignada",
            "mensaje": "Te han asignado la tarea 'Armado de estructura de acero'",
            "leida": True,
            "datos": {"tarea_id": tareas[1].id if len(tareas) > 1 else None},
            "creado_en": datetime.utcnow() - timedelta(days=15)
        },
        {
            "usuario_id": usuarios[1].id,  # Juan Martinez
            "tipo": "tarea_vencida",
            "titulo": "Tarea vencida",
            "mensaje": "La tarea 'Revisión de planos arquitectónicos' ha vencido",
            "leida": False,
            "datos": {"tarea_id": tareas[3].id if len(tareas) > 3 else None},
            "creado_en": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "usuario_id": usuarios[1].id,
            "tipo": "alerta_presupuesto",
            "titulo": "Alerta de presupuesto",
            "mensaje": "El proyecto 'Casa Martinez #23' ha alcanzado el 85% del presupuesto",
            "leida": False,
            "datos": {"proyecto_id": "casa-001", "porcentaje": 85.0},
            "creado_en": datetime.utcnow() - timedelta(hours=5)
        },
        {
            "usuario_id": usuarios[0].id,  # Admin
            "tipo": "gasto_pendiente",
            "titulo": "Gasto pendiente de validación",
            "mensaje": "Hay un gasto de $15,200.00 pendiente de validación",
            "leida": False,
            "datos": {"costo_id": "costo-001"},
            "creado_en": datetime.utcnow() - timedelta(hours=1)
        },
    ]

    notificaciones = []
    for notif_data in notificaciones_data:
        notif = Notificacion(**notif_data)
        db.add(notif)
        notificaciones.append(notif)

    db.commit()
    print(f"✅ {len(notificaciones)} notificaciones creadas")
    return notificaciones


def main():
    """Función principal"""
    print("🌱 Iniciando seed de datos de prueba...")

    # Inicializar base de datos (crear tablas)
    print("\n📦 Creando tablas en la base de datos...")
    init_db()

    # Crear sesión
    db = SessionLocal()

    try:
        # Verificar si ya hay datos
        from app.modules.auth.models import Usuario
        if db.query(Usuario).count() > 0:
            print("\n⚠️  La base de datos ya contiene datos.")
            respuesta = input("¿Deseas eliminar todos los datos y recrearlos? (s/n): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada")
                return

            # Eliminar todos los datos
            from app.database import drop_db
            print("\n🗑️  Eliminando datos existentes...")
            drop_db()
            init_db()

        # Crear datos - Fase 1
        print("\n👥 Creando usuarios...")
        usuarios = crear_usuarios(db)

        print("\n🏗️  Creando proyectos...")
        proyectos = crear_proyectos(db)

        print("\n💰 Creando costos/gastos...")
        costos = crear_costos(db, proyectos)

        # Crear datos - Fase 2
        print("\n👷 Creando empleados...")
        empleados = crear_empleados(db, usuarios)

        print("\n📋 Creando tareas...")
        tareas = crear_tareas(db, proyectos, usuarios)

        print("\n⏰ Creando registros de horas...")
        registros_horas = crear_registros_horas(db, empleados, proyectos, tareas)

        print("\n🔔 Creando notificaciones...")
        notificaciones = crear_notificaciones(db, usuarios, tareas)

        print("\n" + "="*60)
        print("✅ ¡Seed completado exitosamente!")
        print("="*60)
        print("\n📊 Resumen:")
        print(f"  • {len(usuarios)} usuarios")
        print(f"  • {len(proyectos)} proyectos")
        print(f"  • {len(costos)} costos/gastos")
        print(f"  • {len(empleados)} empleados")
        print(f"  • {len(tareas)} tareas")
        print(f"  • {len(registros_horas)} registros de horas")
        print(f"  • {len(notificaciones)} notificaciones")

        print("\n🔐 Credenciales de prueba:")
        print("\n  Admin:")
        print("    Username: admin")
        print("    Password: admin123")
        print("\n  Gerente:")
        print("    Username: jmartinez")
        print("    Password: gerente123")
        print("\n  Supervisor:")
        print("    Username: mgarcia")
        print("    Password: supervisor123")
        print("\n  Trabajador:")
        print("    Username: plopez")
        print("    Password: trabajador123")

        print("\n🚀 Puedes iniciar el servidor con:")
        print("    uvicorn app.main:app --reload")
        print("\n📚 Documentación en:")
        print("    http://localhost:8000/api/v1/docs")

    except Exception as e:
        print(f"\n❌ Error durante el seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
