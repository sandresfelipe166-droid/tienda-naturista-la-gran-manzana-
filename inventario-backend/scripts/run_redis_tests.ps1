<#
	Ejecuta las pruebas de rate limiter con Redis
	Uso:
		powershell -ExecutionPolicy Bypass -File scripts/run_redis_tests.ps1
		(Opcional) levantar Redis primero con start_redis_docker.ps1
#>

$ErrorActionPreference = "Stop"

# Asegurar venv si existe
$venvActivate = Join-Path $PSScriptRoot "..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) { & $venvActivate }

# Exportar REDIS_URL (los tests ya tienen default, pero lo dejamos explícito)
$env:REDIS_URL = "redis://localhost:6379"

Write-Host "Ejecutando tests de Redis..." -ForegroundColor Cyan
python -m pytest tests/test_redis_rate_limiter.py -v
