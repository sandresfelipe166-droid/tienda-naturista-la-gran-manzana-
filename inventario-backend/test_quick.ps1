# Script para ejecutar tests rápidos sin servicios externos
Write-Host "Activando entorno virtual..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

Write-Host "Ejecutando tests unitarios (sin Redis/servicios externos)..." -ForegroundColor Green
pytest -v -m "not integration" --tb=short --maxfail=3 -x

$exitCode = $LASTEXITCODE
Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "Tests completados exitosamente" -ForegroundColor Green
} else {
    Write-Host "Algunos tests fallaron - revisar salida arriba" -ForegroundColor Yellow
}

exit $exitCode
