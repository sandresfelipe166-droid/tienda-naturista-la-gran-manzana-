#!/bin/bash
# Script de inicio para Render - Ejecuta migraciones y luego inicia el servidor

set -e  # Termina si algún comando falla

echo "=========================================="
echo "🚀 Iniciando aplicación Inventario Backend"
echo "=========================================="

# 1. Verificar variables de entorno críticas
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no está configurada"
    exit 1
fi

echo "✓ Variables de entorno verificadas"

# 2. Ejecutar migraciones de Alembic
echo ""
echo "📦 Ejecutando migraciones de base de datos..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✓ Migraciones aplicadas exitosamente"
else
    echo "❌ ERROR: Falló la ejecución de migraciones"
    exit 1
fi

# 3. Iniciar el servidor
echo ""
echo "🌐 Iniciando servidor Uvicorn..."
echo "=========================================="
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
