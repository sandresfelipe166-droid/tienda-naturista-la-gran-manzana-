# Auditoría rápida del repositorio

Fecha: 15 de noviembre de 2025

Resumen de hallazgos:

1. Archivos duplicados
- Existen múltiples archivos idénticos entre `inventario-backend/` y `inventario-frontend/` (por ejemplo `fix_roles.py`, `fix_roles_final.py`, `check_roles.py`, `respaldo_inventario_pre_migracion.sql` en `respaldos/`).
- Objetivo: Consolidar scripts comunes en un solo lugar para evitar mantenimiento duplicado.

2. Binarios incluidos en el repositorio
- `redis-windows` (ejecutables) están presentes en ambos backend y frontend. Estos archivos binarios no suelen colocarse en Git y aumentan el tamaño del repositorio.
- Acciones recomendadas: Extraerlos y usar Docker, descarga manual, o registrar en `README` cómo obtenerlos. Se agregó `redis-windows/` a `.gitignore`.

3. Dependencias y entorno
- Tests fallan localmente por dependencias del entorno (`ModuleNotFoundError: brotli`) y por falta de un servicio Redis en ejecución.
- Acciones recomendadas: documentar los pasos de setup (crear venv, pip install -r requirements.txt, iniciar Redis o usar Docker Compose).
 - Para ello se creó `DEVELOPMENT_ENV_SETUP.md` con pasos claros para Windows y Linux, y un script de ayuda `scripts/setup_dev.ps1`.

4. Scripts de ayuda y limpieza
- Se añadió `scripts/find_duplicates.py` para detectar ficheros con contenido idéntico y facilitar la remoción o centralización.
 - También se añadió `scripts/setup_dev.ps1` para automatizar la creación del virtualenv y la instalación de dependencias en Windows. Para usarlo en PowerShell: `Set-Location c:\Users\cleiv\Desktop\inventario-app` y luego `.
	 scripts\setup_dev.ps1 -Project all`. Si te sale un error al activar la venv, ejecuta `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y vuelve a intentar.

5. Pruebas automatizadas e integración continua
- Los tests requieren env/servicios. Añadir a CI la instalación de dependencias y arranque de servicios (p. ej., Redis) para asegurar reproducibilidad.

Prioridad de correcciones sugeridas (ordenada):
1. ✅ **COMPLETADO** - Eliminar binarios `redis-windows` del repo y documentar cómo obtenerlos (ver `REDIS_WINDOWS_SETUP.md`). Los binarios fueron removidos y el `.gitignore` ya incluye `redis-windows/`.
2. ✅ **COMPLETADO** - Consolidar scripts duplicados (`fix_roles.py`, `fix_roles_final.py`, `check_roles.py`, `setup_roles.py`, `setup_inventory_roles.py`) a `scripts/shared/` con wrappers en backend/frontend (ver `scripts/README.md`).
3. ✅ **COMPLETADO** - Documentar el setup (`DEVELOPMENT_ENV_SETUP.md`) con pasos para crear el entorno virtual y ejecutar tests y servicios.
4. ✅ **COMPLETADO** - Configurar CI para instalar dependencias y ejecutar tests con Redis y Postgres como servicios (actualizado `.github/workflows/ci.yml` en backend y frontend).
5. Ejecutar linters y mypy en CI (ya incluido en nuevo workflow con `lint-and-format` job) — revisar errores de tipo y estilo y corregir el backlog.

Notas finales:
- Si quieres, aplico los pasos 1 y 2 automáticamente: limpiar `.gitignore` (ya hecho) y consolidar archivos duplicados. Puedo también crear un PR con esos cambios si lo prefieres.
