param(
    [switch]$Recreate
)

$ErrorActionPreference = 'Stop'

# Levanta un contenedor Redis para pruebas locales (Windows + Docker Desktop)
# Uso:
#   powershell -ExecutionPolicy Bypass -File scripts/start_redis_docker.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/start_redis_docker.ps1 -Recreate

$containerName = "inventario_redis"
$image = "redis:7-alpine"

Write-Host "Verificando Docker..." -ForegroundColor Cyan
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($null -eq $dockerCmd) {
  Write-Error "Docker no está disponible en el PATH. Abre Docker Desktop e intenta de nuevo."
  exit 1
}

try {
  docker version | Out-Null
} catch {
  Write-Error "Docker Desktop no está corriendo. Inícialo e intenta de nuevo."
  exit 1
}

if ($Recreate) {
  Write-Host "Recreando contenedor $containerName" -ForegroundColor Yellow
  docker rm -f $containerName 2>$null | Out-Null
}

# ¿Existe el contenedor?
$exists = docker ps -a --format '{{.Names}}' | Where-Object { $_ -eq $containerName }

if ($null -eq $exists) {
  Write-Host "Descargando imagen si es necesario: $image" -ForegroundColor Cyan
  docker pull $image | Out-Null

  Write-Host "Creando y arrancando contenedor $containerName en puerto 6379" -ForegroundColor Green
  docker run -d --name $containerName -p 6379:6379 $image | Out-Null
} else {
  # Asegurar que esté iniciado
  $running = docker ps --format '{{.Names}}' | Where-Object { $_ -eq $containerName }
  if ($null -eq $running) {
    Write-Host "Iniciando contenedor $containerName" -ForegroundColor Green
    docker start $containerName | Out-Null
  } else {
    Write-Host "Contenedor $containerName ya está corriendo" -ForegroundColor Green
  }
}

# Mostrar info
$info = docker ps --filter "name=$containerName" --format 'Name={{.Names}} | Image={{.Image}} | Ports={{.Ports}} | Status={{.Status}}'
Write-Host $info -ForegroundColor Gray

Write-Host ""
Write-Host "Redis listo en: redis://localhost:6379" -ForegroundColor Green
Write-Host "Los tests usarán REDIS_URL=redis://localhost:6379 por defecto" -ForegroundColor DarkGray
