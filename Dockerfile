# Usar una versión oficial y ligera de Python
FROM python:3.10-slim

# Instalar dependencias del sistema necesarias para algunas librerías de imagen (como rembg/PIL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar e instalar las librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código fuente de tu proyecto al contenedor
COPY . .

# Exponer el puerto predeterminado de la app
EXPOSE 5000

# Comando para ejecutar la aplicación con Gunicorn en producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "app:app"]