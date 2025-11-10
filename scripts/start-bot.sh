#!/bin/bash

# Script de inicio para el Bot de Telegram - Mark-I
# Este script configura e inicia el bot de Telegram

set -e  # Salir si hay algún error

echo "🤖 Mark-I - Bot de Telegram"
echo "============================"
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navegar al directorio bot
cd "$(dirname "$0")/../bot"

echo -e "${BLUE}📂 Directorio actual: $(pwd)${NC}"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creando entorno virtual...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✅ Entorno virtual encontrado${NC}"
fi

# Activar entorno virtual
echo -e "${BLUE}🔌 Activando entorno virtual...${NC}"
source venv/bin/activate

# Instalar/actualizar dependencias
echo -e "${BLUE}📥 Instalando dependencias...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo -e "${GREEN}✅ Dependencias instaladas${NC}"
echo ""

# Verificar configuración del bot
echo -e "${BLUE}🔍 Verificando configuración...${NC}"

# Leer variables de entorno del backend
if [ -f "../backend/.env" ]; then
    source "../backend/.env"
    echo -e "${GREEN}✅ Variables de entorno cargadas${NC}"
else
    echo -e "${RED}❌ Error: No se encontró archivo .env en backend/${NC}"
    echo -e "${YELLOW}   Copia backend/.env.example a backend/.env primero${NC}"
    exit 1
fi

# Verificar token de Telegram
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ Error: TELEGRAM_BOT_TOKEN no configurado${NC}"
    echo ""
    echo -e "${YELLOW}📝 Para configurar el bot:${NC}"
    echo -e "   1. Habla con @BotFather en Telegram"
    echo -e "   2. Envía /newbot y sigue las instrucciones"
    echo -e "   3. Copia el token que te proporciona"
    echo -e "   4. Edita backend/.env y establece TELEGRAM_BOT_TOKEN=tu-token"
    echo ""
    exit 1
fi

# Verificar que el backend esté corriendo
echo -e "${BLUE}🔍 Verificando conexión con backend...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend está corriendo${NC}"
else
    echo -e "${YELLOW}⚠️  Backend no está corriendo en http://localhost:8000${NC}"
    echo -e "${YELLOW}   Inicia el backend con: ./scripts/start-dev.sh${NC}"
    echo ""
    read -p "¿Deseas continuar de todas formas? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi
echo ""

# Iniciar bot
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}✅ Todo listo! Iniciando bot...${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "${BLUE}🤖 Bot iniciado en modo polling${NC}"
echo -e "${BLUE}💬 Busca tu bot en Telegram y envía /start${NC}"
echo ""
echo -e "${YELLOW}💡 Presiona Ctrl+C para detener el bot${NC}"
echo ""

# Iniciar bot
python main.py
