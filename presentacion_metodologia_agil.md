# Presentación: Metodología Ágil para el Desarrollo del Backend de Inventario

## Diapositiva 1: Título
**Metodología Ágil Interactiva e Incremental**  
**Aplicada al Desarrollo del Backend de Inventario**  
*Proyecto: Sistema de Gestión de Inventario para Tienda Naturista*  
*Presentado por: [Tu Nombre]*  
*Fecha: [Fecha]*

**Notas para el Presentador:**  
Esta presentación explica cómo aplicamos la metodología Ágil en el desarrollo de un backend robusto para gestión de inventario. El proyecto utiliza FastAPI, PostgreSQL y Redis, enfocándose en funcionalidades como autenticación, gestión de productos, alertas y reportes. Destaca la adaptabilidad de Ágil para proyectos complejos con múltiples stakeholders.

---

## Diapositiva 2: Esquema General de la Metodología Ágil
La metodología Ágil es un enfoque iterativo e incremental para el desarrollo de software. Se basa en ciclos cortos de desarrollo (iteraciones o sprints) que permiten adaptarse a cambios y entregar valor de manera continua.

**Esquema General (Ciclo Ágil):**  
1. **Planificación** → 2. **Análisis y Diseño** → 3. **Implementación** → 4. **Pruebas** → 5. **Despliegue** → 6. **Revisión y Retrospectiva**  
   ↻ Repetir el ciclo para la siguiente iteración

*Diagrama sugerido:* Un círculo con flechas conectando las fases, representando la naturaleza cíclica e incremental.

**Detalles para el Presentador:**  
- Explica que cada sprint dura típicamente 2-4 semanas.  
- Enfatiza la importancia del feedback continuo: después de cada fase, se valida con el cliente.  
- Ejemplo del proyecto: En el sprint 1, nos enfocamos en autenticación básica; en el sprint 2, agregamos gestión de productos, permitiendo entregas incrementales.

---

## Diapositiva 3: Fase 1 - Planificación
**Descripción:** En esta fase se define el alcance del sprint, se priorizan las historias de usuario y se estiman los esfuerzos. Se basa en feedback del cliente y stakeholders.

**Entregable Obtenido:**  
- Lista de historias de usuario priorizadas (e.g., "Como administrador, quiero autenticación JWT para acceder al sistema").  
- Plan de sprint con tareas asignadas (e.g., backlog para módulos de autenticación y gestión de productos).

**Detalles para el Presentador:**  
- Historias de usuario siguen el formato: "Como [rol], quiero [funcionalidad] para [beneficio]".  
- Priorización usando MoSCoW: Must have, Should have, Could have, Won't have.  
- En el proyecto: Historias incluyeron autenticación segura, CRUD de productos con validaciones, y alertas automáticas de stock bajo.  
- Estimación con puntos de historia (e.g., 1-2 puntos para tareas simples como endpoints básicos, 5+ para complejas como integración con Redis para cache).

---

## Diapositiva 4: Fase 2 - Análisis y Diseño
**Descripción:** Se analiza los requisitos detallados, se diseña la arquitectura y se modelan las entidades. Incluye diseño de base de datos y APIs.

**Entregable Obtenido:**  
- Diagramas de entidad-relación (e.g., modelos para Producto, Usuario, Lote).  
- Especificaciones de API (e.g., endpoints RESTful para CRUD de inventario).  
- Prototipos o wireframes si aplica.

**Detalles para el Presentador:**  
- Arquitectura: Backend con FastAPI (Python), PostgreSQL para datos persistentes, Redis para cache y sesiones.  
- Modelos clave del proyecto (basados en app/models/models.py):  
  - Producto: id, nombre, stock_actual, stock_minimo, relaciones con Seccion y Laboratorio.  
  - Usuario: autenticación con roles (e.g., Admin, Vendedor).  
  - Lote: tracking de lotes con fechas de vencimiento.  
  - Alerta: para stock bajo o productos por vencer.  
- APIs: Endpoints RESTful, e.g., GET /productos para listar con paginación, POST /productos para crear.  
- Diseño incremental: Empezamos con modelos básicos, agregando relaciones complejas en iteraciones posteriores.

---

## Diapositiva 5: Fase 3 - Implementación
**Descripción:** Desarrollo del código fuente siguiendo las mejores prácticas. Se implementan funcionalidades como autenticación, gestión de productos y alertas.

**Entregable Obtenido:**  
- Código funcional (e.g., routers FastAPI para productos, autenticación JWT).  
- Migraciones de base de datos (e.g., tablas para laboratorio, sección, producto).  
- Integración de middlewares de seguridad.

**Detalles para el Presentador:**  
- Tecnologías: FastAPI para APIs rápidas, SQLAlchemy para ORM, Pydantic para validaciones.  
- Funcionalidades implementadas:  
  - Autenticación JWT (app/routers/auth.py): Login, registro, cambio de contraseña, con logging de auditoría.  
  - Gestión de Productos (app/routers/productos.py): CRUD completo, búsqueda, filtros por sección/laboratorio, alertas de stock bajo y productos por vencer.  
  - Alertas: Sistema automático para notificar stock mínimo o vencimientos cercanos.  
  - Seguridad: Middlewares para rate limiting, CORS, headers de seguridad.  
- Mejores prácticas: Code reviews, commits frecuentes, uso de Alembic para migraciones.  
- Incremental: Sprint 1: Auth básica; Sprint 2: Productos CRUD; Sprint 3: Alertas y reportes.

---

## Diapositiva 6: Fase 4 - Pruebas
**Descripción:** Se ejecutan pruebas unitarias, de integración y de aceptación para asegurar calidad. Incluye testing automatizado con pytest.

**Entregable Obtenido:**  
- Suite de tests (e.g., tests para autenticación, CRUD de productos).  
- Reportes de cobertura de código.  
- Validación de funcionalidades (e.g., alertas de stock bajo).

**Detalles para el Presentador:**  
- Herramientas: Pytest para unitarias, integración con FastAPI TestClient.  
- Cobertura: Apuntamos a >80% con herramientas como coverage.py.  
- Tipos de tests en el proyecto:  
  - Unitarios: Validar funciones CRUD en app/crud/producto.py.  
  - Integración: Endpoints completos, e.g., login y acceso a productos.  
  - Aceptación: Simular flujos de usuario, como crear producto y verificar alerta.  
- Automatización: Tests corren en CI/CD con GitHub Actions.  
- Beneficio: Detectamos bugs temprano, e.g., validaciones de stock mínimo.

---

## Diapositiva 7: Fase 5 - Despliegue
**Descripción:** Se despliega el software en un entorno de staging o producción. Incluye configuración de Docker y variables de entorno.

**Entregable Obtenido:**  
- Versión desplegada del backend (e.g., API corriendo en servidor con endpoints accesibles).  
- Documentación de despliegue (e.g., comandos para Docker).  
- Monitoreo inicial (e.g., health checks y métricas).

**Detalles para el Presentador:**  
- Despliegue: Usamos Docker para contenerización, docker-compose para servicios (FastAPI, PostgreSQL, Redis).  
- Entornos: Staging para pruebas, producción en cloud (e.g., AWS ECS o similar).  
- Configuración: Variables de entorno para DB URLs, secrets JWT.  
- Monitoreo: Health checks en /health, métricas con Prometheus, logs con ELK stack.  
- En el proyecto: Despliegue incremental, probando cada feature en staging antes de producción.

---

## Diapositiva 8: Fase 6 - Revisión y Retrospectiva
**Descripción:** Se revisa el trabajo completado con el cliente, se recopila feedback y se identifica mejoras para el próximo ciclo.

**Entregable Obtenido:**  
- Demo funcional (e.g., presentación de nuevas features como reportes de inventario).  
- Lista de lecciones aprendidas (e.g., mejoras en seguridad o rendimiento).  
- Ajustes al backlog para la siguiente iteración.

**Detalles para el Presentador:**  
- Demo: Sesión interactiva mostrando la API en acción, e.g., login, agregar producto, ver alertas.  
- Retrospectiva: Qué funcionó bien (e.g., entregas rápidas), qué mejorar (e.g., más tests de integración).  
- Feedback del cliente: Ajustes como agregar más filtros en reportes.  
- En el proyecto: Después de cada sprint, demos con el equipo de la tienda, llevando a mejoras como notificaciones push para alertas.

---

## Diapositiva 9: Por Qué la Metodología Ágil es Adecuada para el Proyecto
**Razones de Adecuación:**
- **Complejidad del Proyecto:** El backend de inventario involucra múltiples módulos (autenticación, productos, ventas, alertas) con relaciones complejas, requiriendo adaptabilidad a cambios.
- **Entrega Incremental:** Permite entregar funcionalidades clave primero (e.g., gestión básica de productos) y agregar complejidades (e.g., alertas automáticas) en iteraciones posteriores.
- **Feedback Continuo:** Ideal para un sistema que interactúa con usuarios finales (vendedores, administradores), permitiendo ajustes basados en retroalimentación real.
- **Gestión de Riesgos:** Reduce riesgos en un proyecto con dependencias técnicas (FastAPI, PostgreSQL, Redis) al validar componentes en ciclos cortos.
- **Escalabilidad:** Facilita la evolución del sistema, como agregar nuevos features (e.g., reportes avanzados) sin replanificar todo el proyecto.

*Comparación con otras metodologías:* A diferencia de Waterfall (rígido y lineal), Ágil permite flexibilidad en un dominio cambiante como gestión de inventario.

**Detalles para el Presentador:**  
- Explica con ejemplos: En Waterfall, si el cliente pide cambiar un modelo de producto tarde, es costoso; en Ágil, se ajusta en el próximo sprint.  
- Beneficios cuantitativos: Tiempo de entrega reducido, mejor calidad por tests continuos.  
- Lección del proyecto: Ágil nos permitió pivotar de un sistema simple a uno con alertas inteligentes basado en feedback.

---

## Diapositiva 10: Conclusión
- La Metodología Ágil Interactiva e Incremental es perfecta para el desarrollo iterativo del backend de inventario.
- Permite entregar valor continuo, adaptarse a requisitos cambiantes y asegurar calidad en cada ciclo.
- Recomendación: Implementar con herramientas como Jira para gestión de sprints y Git para control de versiones.

**Preguntas y Discusión**

**Detalles para el Presentador:**  
- Resume los entregables clave: API funcional, tests, despliegue.  
- Invita a preguntas: "¿Cómo manejaron cambios en requisitos?" (Respuesta: A través de retrospectivas y ajuste de backlog).  
- Cierra enfatizando el éxito del proyecto: Sistema robusto, escalable, listo para producción.

---

*Notas para el Presentador:*  
- Usa imágenes o diagramas para ilustrar el esquema (e.g., ciclo Ágil).  
- Incluye ejemplos específicos del proyecto (e.g., modelos SQLAlchemy como Producto con relaciones).  
- Tiempo estimado: 10-15 minutos.  
- Prepárate para demos: Muestra código snippets de routers o tests.  
- Enfatiza la importancia de comunicación: Daily stand-ups, aunque no mencionados, fueron clave.  
- Si hay tiempo, menciona herramientas adicionales: GitHub para repositorio, Pre-commit para linting.
