$ErrorActionPreference = 'Stop'

$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) { Write-Error 'Docker no está disponible en PATH'; exit 1 }

Write-Host 'Deteniendo stack...' -ForegroundColor Yellow

docker compose -f ..\docker-compose.yml down -v

Write-Host 'Listo.' -ForegroundColor Green