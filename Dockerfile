# Dockerfile

FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de la aplicación
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto donde correrá la app
EXPOSE 5001

# Comando para correr la aplicación con uWSGI
CMD ["uwsgi", "--ini", "uwsgi.ini"]
