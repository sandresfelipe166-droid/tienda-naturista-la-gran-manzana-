# Script para generar iconos PWA desde logo.png
# Requisitos: ImageMagick instalado (https://imagemagick.org/script/download.php)

$sourceLogo = "../public/images/logo.png"
$publicDir = "../public"

Write-Host "🎨 Generando iconos PWA desde logo.png..." -ForegroundColor Cyan

# Verificar si existe ImageMagick
$magickCommand = Get-Command magick -ErrorAction SilentlyContinue

if (-not $magickCommand) {
    Write-Host "❌ ImageMagick no está instalado." -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 OPCIÓN 1: Instalar ImageMagick" -ForegroundColor Yellow
    Write-Host "   1. Descargar desde: https://imagemagick.org/script/download.php#windows"
    Write-Host "   2. Instalar (marcar 'Add to PATH')"
    Write-Host "   3. Reiniciar PowerShell y ejecutar este script de nuevo"
    Write-Host ""
    Write-Host "🌐 OPCIÓN 2: Usar herramienta online (más fácil)" -ForegroundColor Green
    Write-Host "   1. Ve a: https://realfavicongenerator.net/"
    Write-Host "   2. Sube: $sourceLogo"
    Write-Host "   3. Genera y descarga el paquete"
    Write-Host "   4. Extrae los archivos a: $publicDir"
    Write-Host ""
    Write-Host "🔧 OPCIÓN 3: Usar logo.png como temporal" -ForegroundColor Cyan
    Write-Host "   Los iconos se crearán copiando logo.png (no optimizado pero funcional)"
    Write-Host ""
    
    $choice = Read-Host "¿Usar OPCIÓN 3 (copiar logo.png)? (s/n)"
    
    if ($choice -eq 's' -or $choice -eq 'S') {
        Write-Host "📋 Copiando logo.png como iconos temporales..." -ForegroundColor Yellow
        
        Copy-Item -Path $sourceLogo -Destination "$publicDir/icon-192.png" -Force
        Copy-Item -Path $sourceLogo -Destination "$publicDir/icon-512.png" -Force
        Copy-Item -Path $sourceLogo -Destination "$publicDir/apple-touch-icon.png" -Force
        Copy-Item -Path $sourceLogo -Destination "$publicDir/favicon.png" -Force
        
        Write-Host "✅ Iconos temporales creados (mismo tamaño que logo.png)" -ForegroundColor Green
        Write-Host "⚠️  RECOMENDACIÓN: Usa realfavicongenerator.net para iconos optimizados" -ForegroundColor Yellow
    } else {
        Write-Host "Cancelado. Por favor instala ImageMagick o usa la opción online." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✅ ImageMagick encontrado. Generando iconos..." -ForegroundColor Green
    
    # Generar iconos en diferentes tamaños
    magick convert $sourceLogo -resize 16x16 "$publicDir/favicon-16.png"
    magick convert $sourceLogo -resize 32x32 "$publicDir/favicon-32.png"
    magick convert $sourceLogo -resize 192x192 "$publicDir/icon-192.png"
    magick convert $sourceLogo -resize 512x512 "$publicDir/icon-512.png"
    magick convert $sourceLogo -resize 180x180 "$publicDir/apple-touch-icon.png"
    
    # Crear favicon.ico (multi-tamaño)
    magick convert $sourceLogo -define icon:auto-resize=16,32,48 "$publicDir/favicon.ico"
    
    Write-Host "✅ Iconos generados exitosamente:" -ForegroundColor Green
    Write-Host "   - favicon.ico (16, 32, 48)" -ForegroundColor Gray
    Write-Host "   - icon-192.png" -ForegroundColor Gray
    Write-Host "   - icon-512.png" -ForegroundColor Gray
    Write-Host "   - apple-touch-icon.png" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🔄 Siguiente paso: Actualizar manifest.json e index.html" -ForegroundColor Cyan
Write-Host "   (El script principal hará esto automáticamente)" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ ¡Iconos listos!" -ForegroundColor Green
