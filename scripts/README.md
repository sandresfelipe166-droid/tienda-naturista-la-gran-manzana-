# Scripts de Utilidad y Mantenimiento

Esta carpeta contiene scripts compartidos y utilidades para administrar el inventario:

## Scripts de roles (`scripts/shared/`)
Estos scripts ayudan a configurar y mantener los roles de usuario en la base de datos.

### `check_roles.py`
Verifica los roles actuales en la base de datos.

**Uso:**
```powershell
# desde inventario-backend o inventario-frontend
python check_roles.py
```

### `fix_roles.py`
Configura los 3 roles principales del sistema (admin, gestor, viewer) eliminando cualquier rol innecesario.

**Uso:**
```powershell
python fix_roles.py
```

### `fix_roles_final.py`
Limpia roles antiguos (rol 4) migrando usuarios y dejando solo 3 roles activos. Muestra cantidad de usuarios por rol.

**Uso:**
```powershell
python fix_roles_final.py
```

### `setup_roles.py`
Crea o actualiza el rol "vendedor" (útil si migraste desde un sistema anterior).

**Uso:**
```powershell
python setup_roles.py
```

### `setup_inventory_roles.py`
Configura roles para gestión de inventario (admin, gestor, viewer), eliminando roles no necesarios.

**Uso:**
```powershell
python setup_inventory_roles.py
```

## Scripts de desarrollo

### `find_duplicates.py`
Escanea el repositorio en busca de archivos duplicados (mismo contenido). Útil para limpieza.

**Uso:**
```powershell
python scripts/find_duplicates.py
```

### `consolidate_scripts.py`
Herramienta usada una vez para mover scripts duplicados entre backend y frontend a `scripts/shared/`. Ya ejecutado.

### `setup_dev.ps1` (PowerShell)
Automatiza la creación de virtualenvs y la instalación de dependencias (Windows).

**Uso:**
```powershell
# Desde la raíz del repo
.\scripts\setup_dev.ps1 -Project all     # backend + frontend
.\scripts\setup_dev.ps1 -Project backend # solo backend
.\scripts\setup_dev.ps1 -Project frontend # solo frontend
```

## Arquitectura de scripts compartidos
Los scripts en `scripts/shared/` usan `_utils.py` para auto-detectar si deben importar desde `inventario-backend` o `inventario-frontend`. Los wrappers en cada subcarpeta (`inventario-backend/fix_roles.py`) simplemente llaman al script compartido.

Esto evita duplicación de código y asegura que el comportamiento sea consistente entre backend y frontend.

---

**Recomendación**: Ejecuta `check_roles.py` después de cualquier script de roles para verificar el estado final.
