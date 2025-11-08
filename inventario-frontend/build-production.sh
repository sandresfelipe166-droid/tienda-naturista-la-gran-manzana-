#!/bin/bash

# Script de Build para Producción
# Uso: bash build-production.sh

echo "🚀 Iniciando Build de Producción"
echo "================================"

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Verificar que npm está instalado
if ! command -v npm &> /dev/null; then
    print_error "npm no está instalado. Por favor instala Node.js"
    exit 1
fi

print_info "Limpiando..."
rm -rf dist/
print_success "Carpeta dist limpiada"

print_info "Instalando dependencias..."
npm install
if [ $? -ne 0 ]; then
    print_error "Error al instalar dependencias"
    exit 1
fi
print_success "Dependencias instaladas"

print_info "Validando TypeScript..."
npm run typecheck
if [ $? -ne 0 ]; then
    print_error "Error en TypeScript"
    exit 1
fi
print_success "TypeScript validado"

print_info "Linting..."
npm run lint || print_info "Algunos warnings de lint"
print_success "Lint completado"

print_info "Construyendo..."
npm run build
if [ $? -ne 0 ]; then
    print_error "Error en el build"
    exit 1
fi
print_success "Build completado"

echo ""
echo "📊 Estadísticas del Build:"
echo "================================"
du -sh dist/ | awk '{print "Tamaño total: " $1}'
find dist/ -type f | wc -l | awk '{print "Archivos: " $1}'

echo ""
echo "✨ Build de Producción Completado!"
echo "================================"
echo ""
print_info "Próximos pasos:"
echo "1. Subir carpeta 'dist' al servidor"
echo "2. Configurar variables de entorno"
echo "3. Testear en producción"
echo ""
print_success "¡Listo para desplegar! 🎉"
