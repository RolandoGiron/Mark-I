"""
Configuración del Bot de Telegram
"""
import os
from dotenv import load_dotenv

load_dotenv()


class BotConfig:
    """Configuración del bot"""

    # Token del bot de Telegram
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # URL del backend API
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

    # Usuario admin para el bot (optional)
    ADMIN_USER_ID = os.getenv("BOT_ADMIN_USER_ID", "")

    # Configuración del bot
    POLL_INTERVAL = int(os.getenv("BOT_POLL_INTERVAL", "1"))  # segundos

    @classmethod
    def validate(cls):
        """Valida que la configuración sea correcta"""
        if not cls.BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en .env")
        return True


config = BotConfig()
