#!/bin/bash

# Esperar a que la base de datos esté lista
echo "Esperando a que MySQL esté listo..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "MySQL está listo!"

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate --noinput

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Cargar datos iniciales (opcional)
# echo "Cargando localidades..."
# python manage.py loaddata eventos/fixtures/localidades.json

# Crear superusuario si no existe (opcional)
# echo "from eventos.models import Usuario; Usuario.objects.create_superuser('admin@nf1.com', 'Admin', 'User', 'admin123') if not Usuario.objects.filter(email='admin@nf1.com').exists() else None" | python manage.py shell

# Iniciar Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
