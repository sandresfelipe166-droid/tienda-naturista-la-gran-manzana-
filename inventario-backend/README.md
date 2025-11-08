# Inventario Backend API

Backend para sistema de gestión de inventario de tienda naturista, desarrollado con FastAPI y SQLAlchemy.

## 🚀 Características

- **API RESTful** con FastAPI
- **Autenticación JWT** con roles y permisos
- **Base de datos PostgreSQL** con migraciones Alembic
- **Sistema de alertas** para stock bajo y productos próximos a vencer
- **Gestión de productos** con lotes y fechas de vencimiento
- **Middleware de seguridad** (CORS, Rate Limiting, Validación)
- **Documentación automática** con Swagger/OpenAPI
- **Tests automatizados** con pytest

## 📋 Prerrequisitos

- Python 3.8+
- PostgreSQL 12+
- Redis (opcional, para caché)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd inventario-backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Configurar base de datos
```bash
# Crear base de datos PostgreSQL
createdb inventario

# Ejecutar migraciones
alembic upgrade head
```

### 6. Ejecutar la aplicación
```bash
# Desarrollo
uvicorn main:app --reload

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentación API

Una vez ejecutada la aplicación, la documentación estará disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Estructura del Proyecto

```
inventario-backend/
├── app/
│   ├── api/v1/          # Versionado de API
│   ├── core/            # Configuración y middlewares
│   ├── crud/            # Operaciones CRUD
│   ├── models/          # Modelos SQLAlchemy
│   ├── routers/         # Endpoints de API
│   ├── services/        # Lógica de negocio
│   └── utils/           # Utilidades
├── alembic/             # Migraciones de BD
├── tests/               # Tests automatizados
├── logs/                # Archivos de log
└── scripts/             # Scripts de utilidad
```

## 🔐 Autenticación

El sistema utiliza JWT para autenticación. Para acceder a endpoints protegidos:

1. **Login**: POST `/api/v1/auth/login`
2. **Obtener token**: Incluir `Authorization: Bearer <token>` en headers

### Roles disponibles:
- **admin**: Acceso completo
- **vendedor**: Acceso a ventas y productos
- **almacen**: Acceso a inventario

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests con cobertura
pytest --cov=app

# Ejecutar tests específicos
pytest tests/test_productos_auth.py
```

## 🚀 Despliegue

### Docker (recomendado)
```bash
# Construir imagen
docker build -t inventario-backend .

# Ejecutar contenedor
docker run -p 8000:8000 inventario-backend
```

### Variables de entorno para producción
```bash
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql+psycopg2://user:pass@host:port/db
```

## 📊 Monitoreo

- **Health Check**: GET `/api/v1/health`
- **DB Health**: GET `/api/v1/db-health`
- **Logs**: Configurados en `logs/app.log`

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

## 🆘 Soporte

Para soporte técnico o preguntas:
- Crear issue en GitHub
- Contactar al equipo de desarrollo
