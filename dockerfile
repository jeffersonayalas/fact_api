# Usar la imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto donde correrá FastAPI
EXPOSE 8080

# Configurar variables de entorno para PostgreSQL
ENV DB_DRIVER="postgresql"
ENV DB_USER="fran"
ENV DB_PASSWORD="7448280"
ENV DB_HOST="172.17.0.1"
ENV DB_PORT="5432"
ENV DB_NAME="data_facturas2"

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
