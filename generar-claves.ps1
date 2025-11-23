# Script para generar claves de seguridad para Railway
# Ejecuta este script para obtener tus SECRET_KEY y CSRF_SECRET

Write-Host "`n🔐 GENERANDO CLAVES DE SEGURIDAD PARA RAILWAY`n" -ForegroundColor Cyan

# Generar SECRET_KEY
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
Write-Host "SECRET_KEY (Copia esto en Railway):" -ForegroundColor Green
Write-Host $secretKey -ForegroundColor Yellow

Write-Host "`n"

# Generar CSRF_SECRET
$csrfSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
Write-Host "CSRF_SECRET (Copia esto en Railway):" -ForegroundColor Green
Write-Host $csrfSecret -ForegroundColor Yellow

Write-Host "`n✅ Guarda estas claves en un lugar seguro!`n" -ForegroundColor Cyan
Write-Host "📋 Cópialas en Railway Dashboard → Variables`n" -ForegroundColor White

# Guardar en archivo temporal (opcional)
$output = @"
# CLAVES GENERADAS - $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# NO COMPARTAS ESTE ARCHIVO

SECRET_KEY=$secretKey
CSRF_SECRET=$csrfSecret
"@

$output | Out-File -FilePath ".\CLAVES_SEGURIDAD.txt" -Encoding UTF8
Write-Host "💾 También guardadas en: CLAVES_SEGURIDAD.txt" -ForegroundColor Magenta
Write-Host "⚠️  IMPORTANTE: No subas este archivo a GitHub!`n" -ForegroundColor Red
