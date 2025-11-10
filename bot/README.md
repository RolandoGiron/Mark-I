# Bot de Telegram - Mark-I

Bot de Telegram para gestionar proyectos de construcción desde el móvil.

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno en `.env`:
```
TELEGRAM_BOT_TOKEN=tu_token_de_bot_father
API_BASE_URL=http://localhost:8000/api/v1
BOT_POLL_INTERVAL=1
```

3. Obtener un token de BotFather:
   - Hablar con [@BotFather](https://t.me/botfather) en Telegram
   - Crear un nuevo bot con `/newbot`
   - Copiar el token y agregarlo al `.env`

## Ejecución

```bash
python -m bot.main
```

O desde el directorio raíz:
```bash
python bot/main.py
```

## Comandos Disponibles

### Autenticación
- `/start` - Mensaje de bienvenida
- `/login <usuario> <contraseña>` - Iniciar sesión

### Proyectos
- `/proyectos` - Lista tus proyectos activos
- `/proyecto <código>` - Información de un proyecto específico

### Tareas
- `/mistareas` - Tus tareas asignadas
- `/tareas` - Lista todas las tareas
- `/tareas proyecto:<código>` - Tareas de un proyecto
- `/tareas estado:<estado>` - Tareas por estado
- `/tareashoy` - Tareas que vencen hoy

### Otros
- `/ayuda` - Muestra la ayuda

## Ejemplos de Uso

```
/login admin admin123
/proyectos
/proyecto CASA-001
/mistareas
/tareas proyecto:CASA-001
/tareas estado:pendiente
/tareashoy
```

## Arquitectura

- `main.py` - Punto de entrada del bot
- `config.py` - Configuración del bot
- `handlers.py` - Handlers de comandos
- `api_client.py` - Cliente HTTP para comunicarse con el backend

## Notas

- El bot se comunica con el backend a través de la API REST
- Los tokens de sesión se almacenan en memoria (en producción usar Redis o DB)
- Los usuarios deben iniciar sesión con sus credenciales del backend
