#!/bin/bash
# Script de build para Render Frontend

set -e  # Termina si algún comando falla

echo "=========================================="
echo "🎨 Construyendo Frontend de Inventario"
echo "=========================================="

# 1. Verificar que Node.js esté instalado
if ! command -v node &> /dev/null; then
    echo "❌ ERROR: Node.js no está instalado"
    exit 1
fi

echo "✓ Node.js $(node --version)"
echo "✓ npm $(npm --version)"

# 2. Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
npm ci --legacy-peer-deps

if [ $? -eq 0 ]; then
    echo "✓ Dependencias instaladas exitosamente"
else
    echo "❌ ERROR: Falló la instalación de dependencias"
    exit 1
fi

# 3. Construir el proyecto
echo ""
echo "🔨 Construyendo proyecto..."
npm run build

if [ $? -eq 0 ]; then
    echo "✓ Proyecto construido exitosamente"
else
    echo "❌ ERROR: Falló la construcción del proyecto"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Build completado exitosamente"
echo "=========================================="
