# Script de Build para Producción - Windows PowerShell
# Uso: .\build-production.ps1

Write-Host "🚀 Iniciando Build de Producción" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Función para imprimir
function Print-Success {
    Write-Host "✅ $args" -ForegroundColor Green
}

function Print-Error {
    Write-Host "❌ $args" -ForegroundColor Red
}

function Print-Info {
    Write-Host "ℹ️  $args" -ForegroundColor Yellow
}

# Verificar que npm está instalado
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Print-Error "npm no está instalado. Por favor instala Node.js"
    exit 1
}

Print-Info "Limpiando..."
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist" | Out-Null
}
Print-Success "Carpeta dist limpiada"

Print-Info "Instalando dependencias..."
npm install
if ($LASTEXITCODE -ne 0) {
    Print-Error "Error al instalar dependencias"
    exit 1
}
Print-Success "Dependencias instaladas"

Print-Info "Validando TypeScript..."
npm run typecheck
if ($LASTEXITCODE -ne 0) {
    Print-Error "Error en TypeScript"
    exit 1
}
Print-Success "TypeScript validado"

Print-Info "Linting..."
npm run lint
if ($LASTEXITCODE -ne 0) {
    Print-Info "Algunos warnings de lint (continuando...)"
}
Print-Success "Lint completado"

Print-Info "Construyendo..."
npm run build
if ($LASTEXITCODE -ne 0) {
    Print-Error "Error en el build"
    exit 1
}
Print-Success "Build completado"

Write-Host ""
Write-Host "📊 Estadísticas del Build:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Calcular tamaño
$folderSize = (Get-ChildItem -Path "dist" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Tamaño total: $([Math]::Round($folderSize, 2)) MB"

# Contar archivos
$fileCount = (Get-ChildItem -Path "dist" -Recurse -File).Count
Write-Host "Archivos: $fileCount"

Write-Host ""
Write-Host "✨ Build de Producción Completado!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Print-Info "Próximos pasos:"
Write-Host "1. Subir carpeta 'dist' al servidor" -ForegroundColor White
Write-Host "2. Configurar variables de entorno" -ForegroundColor White
Write-Host "3. Testear en producción" -ForegroundColor White
Write-Host ""
Print-Success "¡Listo para desplegar! 🎉"

Write-Host ""
Print-Info "Para previsualizar localmente, ejecuta:"
Write-Host "npm run preview" -ForegroundColor Cyan
