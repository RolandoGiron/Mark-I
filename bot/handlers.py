"""
Handlers de comandos del Bot de Telegram
"""
from telegram import Update
from telegram.ext import ContextTypes
from bot.api_client import api_client
from typing import Dict


# Storage simple para tokens de usuario (en producción usar Redis o DB)
user_tokens: Dict[int, str] = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /start"""
    user = update.effective_user
    welcome_message = f"""
Hola {user.first_name}! Bienvenido al Bot de Mark-I

Soy tu asistente para gestionar proyectos de construcción.

Para comenzar, necesitas iniciar sesión con:
/login <usuario> <contraseña>

Comandos disponibles:
/ayuda - Muestra esta ayuda
/login <usuario> <contraseña> - Inicia sesión
/proyectos - Lista tus proyectos
/proyecto <código> - Info de un proyecto
/mistares - Tus tareas asignadas
/tareas - Lista todas las tareas
/tareashoy - Tareas que vencen hoy

Para más información: /ayuda
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /ayuda"""
    help_text = """
📋 *Comandos Disponibles*

*Autenticación:*
/start - Mensaje de bienvenida
/login <usuario> <contraseña> - Iniciar sesión

*Proyectos:*
/proyectos - Lista tus proyectos activos
/proyecto <código> - Información de un proyecto específico

*Tareas:*
/mistareas - Tus tareas asignadas
/tareas - Lista todas las tareas
/tareas proyecto:<código> - Tareas de un proyecto
/tareas estado:<estado> - Tareas por estado
/tareashoy - Tareas que vencen hoy

*Otros:*
/ayuda - Muestra esta ayuda

Estados válidos: pendiente, en_progreso, completada, cancelada
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /login"""
    user_id = update.effective_user.id

    if len(context.args) != 2:
        await update.message.reply_text(
            "Uso: /login <usuario> <contraseña>\n"
            "Ejemplo: /login admin admin123"
        )
        return

    username = context.args[0]
    password = context.args[1]

    try:
        # Intentar login
        response = await api_client.login(username, password)
        token = response.get("access_token")

        if token:
            # Guardar token
            user_tokens[user_id] = token
            await update.message.reply_text(
                f"✅ Sesión iniciada correctamente como {username}!\n"
                f"Ahora puedes usar los demás comandos."
            )
        else:
            await update.message.reply_text(
                "❌ Error al iniciar sesión. Intenta de nuevo."
            )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Error al iniciar sesión: {str(e)}\n"
            f"Verifica tus credenciales e intenta de nuevo."
        )


def require_auth(func):
    """Decorador para requerir autenticación"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        token = user_tokens.get(user_id)

        if not token:
            await update.message.reply_text(
                "❌ No has iniciado sesión.\n"
                "Usa /login <usuario> <contraseña> primero."
            )
            return

        # Pasar el token al handler
        context.user_data['token'] = token
        return await func(update, context)

    return wrapper


@require_auth
async def proyectos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /proyectos"""
    token = context.user_data['token']

    try:
        response = await api_client.get_proyectos(token)
        proyectos = response.get("items", [])

        if not proyectos:
            await update.message.reply_text("No se encontraron proyectos.")
            return

        message = "📁 *Tus Proyectos:*\n\n"
        for p in proyectos:
            estado_emoji = {
                "prospecto": "🔵",
                "aprobado": "🟢",
                "en_curso": "🟡",
                "pausado": "🟠",
                "completado": "✅",
                "cancelado": "❌"
            }.get(p['estado'], "")

            message += (
                f"{estado_emoji} *{p['codigo']}* - {p['nombre']}\n"
                f"   Estado: {p['estado']}\n"
                f"   Presupuesto: ${p['presupuesto_total']:.2f}\n\n"
            )

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error al obtener proyectos: {str(e)}")


@require_auth
async def proyecto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /proyecto <código>"""
    token = context.user_data['token']

    if len(context.args) != 1:
        await update.message.reply_text(
            "Uso: /proyecto <código>\n"
            "Ejemplo: /proyecto CASA-001"
        )
        return

    codigo = context.args[0]

    try:
        proyecto = await api_client.get_proyecto_by_codigo(codigo, token)

        if not proyecto:
            await update.message.reply_text(f"❌ No se encontró el proyecto '{codigo}'")
            return

        message = f"""
📁 *Proyecto: {proyecto['nombre']}*

Código: `{proyecto['codigo']}`
Estado: {proyecto['estado']}
Cliente: {proyecto.get('cliente_nombre', 'N/A')}

💰 *Financiero:*
Presupuesto: ${proyecto['presupuesto_total']:.2f}
Ubicación: {proyecto.get('ubicacion', 'N/A')}

📅 *Fechas:*
Inicio: {proyecto.get('fecha_inicio', 'N/A')}
Fin estimado: {proyecto.get('fecha_fin_estimada', 'N/A')}

Descripción:
{proyecto.get('descripcion', 'Sin descripción')}
"""
        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error al obtener proyecto: {str(e)}")


@require_auth
async def mistareas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /mistareas"""
    token = context.user_data['token']

    try:
        tareas = await api_client.get_mis_tareas(token)

        if not tareas:
            await update.message.reply_text("✅ No tienes tareas asignadas.")
            return

        message = "📋 *Tus Tareas Asignadas:*\n\n"
        for t in tareas[:10]:  # Limitar a 10
            prioridad_emoji = {
                "baja": "🔵",
                "media": "🟡",
                "alta": "🔴",
                "urgente": "🚨"
            }.get(t['prioridad'], "")

            estado_emoji = {
                "pendiente": "⏸",
                "en_progreso": "▶️",
                "completada": "✅",
                "cancelada": "❌"
            }.get(t['estado'], "")

            vencimiento = t.get('fecha_vencimiento', 'Sin fecha')
            if vencimiento and vencimiento != 'Sin fecha':
                vencimiento = vencimiento[:10]  # Solo la fecha

            message += (
                f"{estado_emoji} {prioridad_emoji} *{t['titulo']}*\n"
                f"   Estado: {t['estado']}\n"
                f"   Vence: {vencimiento}\n\n"
            )

        if len(tareas) > 10:
            message += f"\n_(Mostrando 10 de {len(tareas)} tareas)_"

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error al obtener tareas: {str(e)}")


@require_auth
async def tareas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /tareas [filtros]"""
    token = context.user_data['token']

    # Parsear filtros
    proyecto_id = None
    estado = None

    for arg in context.args:
        if arg.startswith("proyecto:"):
            # Buscar proyecto por código
            codigo = arg.split(":")[1]
            try:
                proyecto = await api_client.get_proyecto_by_codigo(codigo, token)
                if proyecto:
                    proyecto_id = proyecto['id']
            except:
                pass
        elif arg.startswith("estado:"):
            estado = arg.split(":")[1]

    try:
        response = await api_client.get_tareas(token, proyecto_id=proyecto_id, estado=estado)
        tareas = response.get("items", [])

        if not tareas:
            await update.message.reply_text("No se encontraron tareas con los filtros especificados.")
            return

        filtros_str = ""
        if proyecto_id:
            filtros_str += f"Proyecto: {codigo}\n"
        if estado:
            filtros_str += f"Estado: {estado}\n"

        message = "📋 *Tareas:*\n"
        if filtros_str:
            message += f"\n{filtros_str}\n"

        for t in tareas[:10]:  # Limitar a 10
            prioridad_emoji = {
                "baja": "🔵",
                "media": "🟡",
                "alta": "🔴",
                "urgente": "🚨"
            }.get(t['prioridad'], "")

            estado_emoji = {
                "pendiente": "⏸",
                "en_progreso": "▶️",
                "completada": "✅",
                "cancelada": "❌"
            }.get(t['estado'], "")

            message += (
                f"{estado_emoji} {prioridad_emoji} *{t['titulo']}*\n"
                f"   {t['estado']} - {t.get('asignado_a_id', 'Sin asignar')}\n\n"
            )

        total = response.get("total", 0)
        if total > 10:
            message += f"\n_(Mostrando 10 de {total} tareas)_"

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error al obtener tareas: {str(e)}")


@require_auth
async def tareashoy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /tareashoy"""
    token = context.user_data['token']

    try:
        tareas = await api_client.get_tareas_hoy(token)

        if not tareas:
            await update.message.reply_text("✅ No hay tareas que venzan hoy.")
            return

        message = "📅 *Tareas que vencen HOY:*\n\n"
        for t in tareas:
            prioridad_emoji = {
                "baja": "🔵",
                "media": "🟡",
                "alta": "🔴",
                "urgente": "🚨"
            }.get(t['prioridad'], "")

            message += (
                f"{prioridad_emoji} *{t['titulo']}*\n"
                f"   Estado: {t['estado']}\n"
                f"   Prioridad: {t['prioridad']}\n\n"
            )

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Error al obtener tareas: {str(e)}")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comandos desconocidos"""
    await update.message.reply_text(
        "❌ Comando no reconocido.\n"
        "Usa /ayuda para ver los comandos disponibles."
    )
