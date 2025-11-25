# Paso a Paso: Desplegar Docker en Railway

## Opción 1: Despliegue Automático con Dockerfile (Recomendado)

Railway detecta automáticamente el `Dockerfile` y construye la imagen.

### 1. Preparar el Repositorio

```bash
# Asegúrate de que todos los archivos estén commiteados
git add .
git commit -m "Add Docker configuration"
git push origin main
```

### 2. Crear Proyecto en Railway

1. Ve a https://railway.app
2. Haz clic en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway a acceder a tu GitHub
5. Selecciona tu repositorio `nf1`

### 3. Agregar Base de Datos MySQL

1. En tu proyecto Railway, haz clic en **"+ New"**
2. Selecciona **"Database"** → **"Add MySQL"**
3. Railway creará automáticamente las variables:
   - `MYSQL_ROOT_PASSWORD`
   - `MYSQL_DATABASE`
   - `MYSQL_USER`
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_URL`

### 4. Configurar Variables de Entorno del Servicio Web

En el servicio de tu aplicación Django (web), ve a **Variables** y agrega:

```bash
# Django Configuration
SECRET_KEY=<genera-una-clave-segura>
DEBUG=False
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
CSRF_TRUSTED_ORIGINS=https://${{RAILWAY_PUBLIC_DOMAIN}}

# Database (usar referencias de MySQL)
DB_NAME=${{MYSQL_DATABASE}}
DB_USER=${{MYSQL_USER}}
DB_PASSWORD=${{MYSQL_ROOT_PASSWORD}}
DB_HOST=${{MYSQL_HOST}}
DB_PORT=${{MYSQL_PORT}}

# Railway variables (automáticas)
PORT=8000
```

**Generar SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Modificar Dockerfile para Railway (Importante)

Railway usa el `PORT` variable. Actualiza el `CMD` en `Dockerfile`:

```dockerfile
# Cambiar la última línea de:
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

# A:
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

O crear un archivo `railway.json`:

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 6. Conectar Servicio Web con Base de Datos

1. En el servicio **web**, ve a **Settings**
2. En **Service Dependencies**, conecta con el servicio **MySQL**
3. Railway configurará automáticamente las referencias de variables

### 7. Esperar el Despliegue

Railway construirá la imagen Docker automáticamente. Puedes ver el progreso en:
- **Deployments** → Ver logs en tiempo real

### 8. Ejecutar Migraciones

Una vez desplegado, ejecuta desde Railway CLI o dashboard:

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Vincular al proyecto
railway link

# Ejecutar migraciones
railway run python manage.py migrate

# Crear superusuario
railway run python manage.py createsuperuser

# Cargar datos iniciales
railway run python manage.py loaddata eventos/fixtures/localidades.json
```

### 9. Verificar Despliegue

1. Ve a **Settings** → **Domains**
2. Railway genera un dominio automáticamente: `tu-app.up.railway.app`
3. Haz clic en el enlace para abrir tu aplicación
4. Prueba el login y funcionalidades

---

## Opción 2: Docker Compose en Railway (No recomendado)

Railway no soporta `docker-compose.yml` nativamente. Usa la Opción 1.

---

## Opción 3: Despliegue Manual desde Imagen Docker Hub

### 1. Construir y Subir Imagen a Docker Hub

```bash
# Build
docker build -t tu-usuario/nf1:latest .

# Login a Docker Hub
docker login

# Push
docker push tu-usuario/nf1:latest
```

### 2. En Railway

1. Nuevo proyecto → **"Deploy Docker Image"**
2. Ingresar: `tu-usuario/nf1:latest`
3. Configurar variables de entorno (igual que Opción 1)

---

## Configuración Adicional

### Actualizar `settings.py` para Railway

Asegúrate de tener en `config/settings.py`:

```python
import os

# Railway proporciona PORT automáticamente
PORT = os.getenv('PORT', '8000')

# Usar RAILWAY_PUBLIC_DOMAIN para ALLOWED_HOSTS
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN', '')
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
```

### Script de Inicialización Automática

Crear `railway-init.sh`:

```bash
#!/bin/bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

Y en `railway.json`:

```json
{
  "deploy": {
    "startCommand": "bash railway-init.sh"
  }
}
```

---

## Troubleshooting

### Error: Application failed to respond

**Causa**: Railway no puede conectarse al puerto.

**Solución**: Asegúrate de usar `$PORT` en Gunicorn:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### Error: DisallowedHost

**Causa**: Dominio de Railway no está en `ALLOWED_HOSTS`.

**Solución**: Agregar variable:
```bash
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
```

### Error: Can't connect to MySQL

**Causa**: Variables de base de datos incorrectas.

**Solución**: Verificar que las referencias sean correctas:
```bash
DB_HOST=${{MYSQL_HOST}}
DB_PORT=${{MYSQL_PORT}}
```

### Imagen muy grande / Build lento

**Solución**: Optimizar Dockerfile con multi-stage build y `.dockerignore`.

### Migraciones no se aplican

**Solución**: Ejecutar manualmente:
```bash
railway run python manage.py migrate
```

O agregar a `railway-init.sh`.

---

## Monitoreo y Logs

```bash
# Ver logs en tiempo real
railway logs

# Ver logs de un despliegue específico
railway logs --deployment <deployment-id>

# Ver uso de recursos
# Ir a Railway Dashboard → Metrics
```

---

## Comandos Útiles Railway CLI

```bash
# Ver variables
railway variables

# Agregar variable
railway variables set KEY=value

# Ejecutar comando
railway run <comando>

# Shell interactivo
railway run bash

# Abrir en navegador
railway open
```

---

## Resumen de Archivos Necesarios

✅ `Dockerfile` - Define la imagen
✅ `.dockerignore` - Optimiza build
✅ `requirements.txt` - Dependencias Python
✅ `Procfile` o `railway.json` - Comando de inicio (opcional)
✅ `runtime.txt` - Versión Python (opcional)

---

## Checklist Final

- [ ] Dockerfile actualizado con `$PORT`
- [ ] Variables de entorno configuradas en Railway
- [ ] Servicio MySQL creado y conectado
- [ ] SECRET_KEY generado y seguro
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS incluye dominio Railway
- [ ] CSRF_TRUSTED_ORIGINS con https://
- [ ] Migraciones aplicadas
- [ ] Superusuario creado
- [ ] Datos iniciales cargados
- [ ] Aplicación accesible en navegador

---

## Próximos Pasos

1. **Dominio personalizado**: Railway Settings → Domains → Add Custom Domain
2. **CI/CD**: Railway redespliega automáticamente con cada push a main
3. **Backups**: Configurar backups de MySQL en Railway
4. **Monitoreo**: Integrar con Sentry o similar
5. **Escalabilidad**: Ajustar workers de Gunicorn según tráfico
