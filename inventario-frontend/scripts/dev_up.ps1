$ErrorActionPreference = 'Stop'

$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) { Write-Error 'Docker no está disponible en PATH'; exit 1 }

Write-Host 'Levantando stack (Postgres + Redis + Backend)...' -ForegroundColor Cyan

docker compose -f ..\docker-compose.yml up -d --build

Write-Host 'Servicios levantados:' -ForegroundColor Green

docker compose -f ..\docker-compose.yml ps