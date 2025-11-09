FROM python:3.11-slim
WORKDIR /app

# Copiar archivos de dependencias
COPY pyproject.toml requirements.txt ./

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Hacer ejecutable el script de inicio
RUN chmod +x start.sh

# Variables de entorno
ENV PYTHONUNBUFFERED=1

# Exponer puerto
EXPOSE 8000

# Usar el script de inicio que ejecuta migraciones primero
CMD ["./start.sh"]
