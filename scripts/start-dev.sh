#!/bin/bash

# Script de inicio rápido para desarrollo
# Autor: Mark-I Team

echo "🚀 Mark-I - Sistema de Gestión de Obras"
echo "========================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python encontrado: $(python3 --version)${NC}"

# Verificar si existe venv
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}📦 Creando entorno virtual...${NC}"
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activar venv
echo -e "${GREEN}🔧 Activando entorno virtual...${NC}"
source backend/venv/bin/activate

# Instalar dependencias
if [ ! -f "backend/venv/.installed" ]; then
    echo -e "${YELLOW}📚 Instalando dependencias...${NC}"
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    touch backend/venv/.installed
    echo -e "${GREEN}✅ Dependencias instaladas${NC}"
else
    echo -e "${GREEN}✅ Dependencias ya instaladas${NC}"
fi

# Verificar .env
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚙️  Creando archivo .env desde .env.example...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✅ Archivo .env creado${NC}"
    echo -e "${YELLOW}⚠️  Recuerda actualizar el SECRET_KEY en backend/.env${NC}"
else
    echo -e "${GREEN}✅ Archivo .env encontrado${NC}"
fi

# Verificar si hay datos en la BD
if [ ! -f "backend/obras.db" ]; then
    echo -e "${YELLOW}🌱 Base de datos vacía. ¿Deseas crear datos de prueba? (s/n)${NC}"
    read -r response
    if [[ "$response" == "s" || "$response" == "S" ]]; then
        echo -e "${GREEN}📊 Creando datos de prueba...${NC}"
        cd backend
        python scripts/seed_data.py
        cd ..
    fi
fi

# Iniciar servidor
echo ""
echo -e "${GREEN}🎉 ¡Listo! Iniciando servidor...${NC}"
echo ""
echo "📍 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/api/v1/docs"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener el servidor${NC}"
echo ""

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
