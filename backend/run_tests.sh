#!/bin/bash

# Script para ejecutar tests del backend Mark-I
# Uso: ./run_tests.sh [opción]

set -e

cd "$(dirname "$0")"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}  Mark-I Backend Test Suite${NC}"
echo -e "${BLUE}=================================${NC}\n"

# Función para mostrar ayuda
show_help() {
    echo "Uso: ./run_tests.sh [opción]"
    echo ""
    echo "Opciones:"
    echo "  all          - Ejecutar todos los tests (default)"
    echo "  auth         - Solo tests de autenticación"
    echo "  proyectos    - Solo tests de proyectos"
    echo "  costos       - Solo tests de costos"
    echo "  system       - Solo tests del sistema"
    echo "  cov          - Ejecutar con reporte de cobertura"
    echo "  html         - Generar reporte HTML de cobertura"
    echo "  fast         - Ejecutar sin tests lentos"
    echo "  help         - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./run_tests.sh              # Todos los tests"
    echo "  ./run_tests.sh auth         # Solo autenticación"
    echo "  ./run_tests.sh cov          # Con cobertura"
}

# Verificar instalación de pytest
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest no está instalado${NC}"
    echo "Ejecuta: pip install -r requirements.txt"
    exit 1
fi

# Procesar argumentos
case "${1:-all}" in
    all)
        echo -e "${GREEN}Ejecutando todos los tests...${NC}\n"
        pytest -v
        ;;
    auth)
        echo -e "${GREEN}Ejecutando tests de autenticación...${NC}\n"
        pytest tests/test_auth.py -v
        ;;
    proyectos)
        echo -e "${GREEN}Ejecutando tests de proyectos...${NC}\n"
        pytest tests/test_proyectos.py -v
        ;;
    costos)
        echo -e "${GREEN}Ejecutando tests de costos...${NC}\n"
        pytest tests/test_costos.py -v
        ;;
    system)
        echo -e "${GREEN}Ejecutando tests del sistema...${NC}\n"
        pytest tests/test_system.py -v
        ;;
    cov)
        echo -e "${GREEN}Ejecutando tests con cobertura...${NC}\n"
        pytest --cov=app --cov-report=term-missing
        ;;
    html)
        echo -e "${GREEN}Generando reporte HTML de cobertura...${NC}\n"
        pytest --cov=app --cov-report=html
        echo -e "\n${YELLOW}Reporte generado en: htmlcov/index.html${NC}"
        ;;
    fast)
        echo -e "${GREEN}Ejecutando tests rápidos...${NC}\n"
        pytest -v -m "not slow"
        ;;
    help)
        show_help
        ;;
    *)
        echo -e "${RED}Opción no reconocida: $1${NC}\n"
        show_help
        exit 1
        ;;
esac

# Verificar resultado
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Tests completados exitosamente${NC}"
else
    echo -e "\n${RED}✗ Algunos tests fallaron${NC}"
    exit 1
fi
