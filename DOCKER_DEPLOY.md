# Despliegue con Docker

Guía completa para empaquetar y desplegar NF1 con Docker.

## Archivos Docker

- **`Dockerfile`**: Imagen de la aplicación Django
- **`docker-compose.yml`**: Orquestación de servicios (web, db, nginx)
- **`nginx.conf`**: Configuración del proxy inverso Nginx
- **`docker-entrypoint.sh`**: Script de inicialización (migraciones, collectstatic)
- **`.dockerignore`**: Archivos excluidos de la imagen
- **`.env.docker`**: Variables de entorno para Docker Compose

## Arquitectura de Servicios

```
┌─────────────┐
│   Nginx     │ :80  (Proxy Inverso)
│  (Alpine)   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Django    │ :8000 (Gunicorn)
│   (Web)     │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   MySQL     │ :3306
│   (DB)      │
└─────────────┘
```

## Uso Rápido

### 1. Desarrollo Local con Docker

```bash
# Copiar variables de entorno
cp .env.docker .env

# Construir y levantar servicios
docker-compose up --build

# En otra terminal: Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Cargar datos iniciales
docker-compose exec web python manage.py loaddata eventos/fixtures/localidades.json

# Acceder a:
# - Aplicación: http://localhost
# - Admin: http://localhost/admin
```

### 2. Detener Servicios

```bash
# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (base de datos)
docker-compose down -v
```

## Comandos Útiles

### Gestión de Servicios

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f web

# Reiniciar un servicio
docker-compose restart web

# Ejecutar comando en contenedor
docker-compose exec web python manage.py <comando>

# Acceder a shell del contenedor
docker-compose exec web bash

# Acceder a MySQL
docker-compose exec db mysql -u root -p
```

### Migraciones y Datos

```bash
# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Exportar datos
docker-compose exec web python manage.py dumpdata > backup.json

# Importar datos
docker-compose exec web python manage.py loaddata backup.json
```

### Archivos Estáticos y Media

```bash
# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Ver archivos estáticos
docker-compose exec web ls -la staticfiles/

# Ver archivos media
docker-compose exec web ls -la media/
```

## Producción

### Opción 1: Docker Hub

```bash
# 1. Construir imagen
docker build -t tu-usuario/nf1:latest .

# 2. Subir a Docker Hub
docker login
docker push tu-usuario/nf1:latest

# 3. En servidor de producción
docker pull tu-usuario/nf1:latest
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY="tu-secret-key" \
  -e DEBUG="False" \
  -e DB_HOST="tu-host" \
  -e DB_PASSWORD="tu-password" \
  tu-usuario/nf1:latest
```

### Opción 2: Docker Compose en VPS

```bash
# 1. Clonar repositorio en servidor
git clone https://github.com/tu-usuario/nf1.git
cd nf1

# 2. Configurar variables de entorno
nano .env
# Editar: SECRET_KEY, DEBUG=False, DB_PASSWORD, etc.

# 3. Levantar en background
docker-compose up -d

# 4. Aplicar migraciones
docker-compose exec web python manage.py migrate

# 5. Crear superusuario
docker-compose exec web python manage.py createsuperuser

# 6. Configurar firewall
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Opción 3: Railway con Dockerfile

Railway detectará automáticamente el `Dockerfile` y lo usará para construir la imagen.

**Variables de entorno en Railway:**
```bash
SECRET_KEY=tu-clave-segura
DEBUG=False
ALLOWED_HOSTS=tu-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://tu-app.up.railway.app
DB_NAME=${{MYSQL_DATABASE}}
DB_USER=${{MYSQL_USER}}
DB_PASSWORD=${{MYSQL_PASSWORD}}
DB_HOST=${{MYSQL_HOST}}
DB_PORT=${{MYSQL_PORT}}
```

## Optimizaciones de Producción

### Multi-stage Build (Dockerfile optimizado)

```dockerfile
# Stage 1: Builder
FROM python:3.13.9-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.13.9-slim

WORKDIR /app
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### Health Checks

Agregar al `docker-compose.yml`:

```yaml
web:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

### SSL con Let's Encrypt

```bash
# Instalar certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d tudominio.com

# Renovación automática
sudo certbot renew --dry-run
```

## Volúmenes Docker

Los datos persistentes se almacenan en volúmenes:

- **`mysql_data`**: Base de datos MySQL
- **`static_volume`**: Archivos estáticos (CSS, JS, imgs)
- **`media_volume`**: Archivos subidos por usuarios

### Backup de Volúmenes

```bash
# Backup de MySQL
docker-compose exec db mysqldump -u root -p nf1 > backup_$(date +%Y%m%d).sql

# Backup de volumen completo
docker run --rm -v nf1_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql_backup.tar.gz -C /data .

# Restaurar backup
docker run --rm -v nf1_mysql_data:/data -v $(pwd):/backup alpine tar xzf /backup/mysql_backup.tar.gz -C /data
```

## Troubleshooting

### Contenedor web no inicia
```bash
# Ver logs detallados
docker-compose logs web

# Verificar conexión a BD
docker-compose exec web python manage.py dbshell
```

### Error de permisos en archivos estáticos
```bash
# Ajustar permisos
docker-compose exec web chown -R nobody:nogroup staticfiles/
docker-compose exec web chown -R nobody:nogroup media/
```

### MySQL no se conecta
```bash
# Verificar que MySQL está corriendo
docker-compose ps

# Esperar a que MySQL esté listo
docker-compose exec db mysqladmin ping -h localhost -u root -p
```

### Reinicio completo
```bash
# Eliminar todo y empezar de cero
docker-compose down -v
docker-compose up --build
```

## Recursos

- **Dockerfile reference**: https://docs.docker.com/engine/reference/builder/
- **Docker Compose**: https://docs.docker.com/compose/
- **Gunicorn deployment**: https://docs.gunicorn.org/en/stable/deploy.html
- **Nginx optimization**: https://www.nginx.com/blog/tuning-nginx/

## Monitoreo

```bash
# Uso de recursos
docker stats

# Espacio en disco
docker system df

# Limpiar recursos no utilizados
docker system prune -a
```
