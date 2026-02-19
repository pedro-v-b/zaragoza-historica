# Dockerfile para Backend Python con FastAPI
FROM python:3.11-slim

# Instalar dependencias del sistema para psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para uploads
RUN mkdir -p /app/uploads/thumbs

# Exponer puerto
EXPOSE 3000

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV PORT=3000
ENV HOST=0.0.0.0

# Comando para iniciar la aplicación
CMD ["python", "main.py"]
