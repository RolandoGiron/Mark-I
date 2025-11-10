"""
Bot de Telegram para Mark-I
"""
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.config import config
from bot.handlers import (
    start_command,
    help_command,
    login_command,
    proyectos_command,
    proyecto_command,
    mistareas_command,
    tareas_command,
    tareashoy_command,
    unknown_command
)

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Función principal del bot"""
    # Validar configuración
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Error de configuración: {e}")
        return

    # Crear aplicación
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Registrar handlers de comandos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("login", login_command))
    application.add_handler(CommandHandler("proyectos", proyectos_command))
    application.add_handler(CommandHandler("proyecto", proyecto_command))
    application.add_handler(CommandHandler("mistareas", mistareas_command))
    application.add_handler(CommandHandler("tareas", tareas_command))
    application.add_handler(CommandHandler("tareashoy", tareashoy_command))

    # Handler para comandos desconocidos
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Iniciar bot
    logger.info("🤖 Bot de Mark-I iniciado")
    application.run_polling(poll_interval=config.POLL_INTERVAL)


if __name__ == "__main__":
    main()
