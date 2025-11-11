FROM python:3.11-slim

# 1) Sistema base y herramientas de compilación mínimas
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Mejorar pip para compatibilidades de wheels
RUN pip install --upgrade pip

# 3) Instalar dependencias Python usando sólo los archivos de requisitos
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copiar el resto de la app (excluida por .dockerignore lo innecesario)
COPY . .

# 5) Script de arranque (migra y levanta uvicorn)
RUN chmod +x start.sh

# 6) Variables de entorno
ENV PYTHONUNBUFFERED=1

# 7) Exponer puerto
EXPOSE 8000

# 8) Comando final
CMD ["./start.sh"]
