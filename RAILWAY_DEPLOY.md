# Guía de Despliegue en Railway

## Configuración del Proyecto

### 1. Archivos de Configuración Creados

- **`Procfile`**: Define el comando para ejecutar Gunicorn
- **`runtime.txt`**: Especifica la versión de Python (3.13.9)
- **`requirements.txt`**: Actualizado con gunicorn y whitenoise

### 2. Dependencias Agregadas

```
gunicorn==21.2.0    # Servidor WSGI para producción
whitenoise==6.6.0   # Servir archivos estáticos sin necesidad de servidor adicional
```

### 3. Configuración de Settings

- **WhiteNoise**: Middleware agregado para servir archivos estáticos
- **STATIC_ROOT**: Configurado en `/staticfiles/`
- **ALLOWED_HOSTS**: Acepta localhost por defecto, configurable con variable de entorno
- **CSRF_TRUSTED_ORIGINS**: Nueva variable para dominios de producción

## Pasos para Desplegar en Railway

### 1. Preparar Base de Datos MySQL en Railway

1. En tu proyecto Railway, crea un servicio MySQL
2. Railway generará las credenciales automáticamente
3. Anota los siguientes valores:
   - `MYSQL_DATABASE`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_HOST`
   - `MYSQL_PORT`

### 2. Configurar Variables de Entorno en Railway

En la configuración del servicio web, agrega estas variables:

```bash
SECRET_KEY=genera-una-clave-secreta-segura-aqui
DEBUG=False
ALLOWED_HOSTS=tu-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://tu-app.up.railway.app

# Credenciales de MySQL (usar las de Railway)
DB_NAME=${{MYSQL_DATABASE}}
DB_USER=${{MYSQL_USER}}
DB_PASSWORD=${{MYSQL_PASSWORD}}
DB_HOST=${{MYSQL_HOST}}
DB_PORT=${{MYSQL_PORT}}
```

**Nota**: Railway permite usar `${{VARIABLE}}` para referenciar variables del servicio MySQL.

### 3. Generar SECRET_KEY Seguro

Ejecuta en Python:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 4. Inicializar Base de Datos

Una vez desplegado, ejecuta desde Railway CLI o dashboard:

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# (Opcional) Cargar datos iniciales
python manage.py loaddata eventos/fixtures/localidades.json
```

### 5. Recolectar Archivos Estáticos

Railway ejecutará automáticamente:

```bash
python manage.py collectstatic --noinput
```

## Variables de Entorno Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta de Django | `django-insecure-abc123...` |
| `DEBUG` | Modo debug (False en producción) | `False` |
| `ALLOWED_HOSTS` | Dominios permitidos | `app.railway.app,midominio.com` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes CSRF confiables | `https://app.railway.app` |
| `DB_NAME` | Nombre de la base de datos | `railway` |
| `DB_USER` | Usuario MySQL | `root` |
| `DB_PASSWORD` | Contraseña MySQL | `password123` |
| `DB_HOST` | Host MySQL | `containers-us-west.railway.app` |
| `DB_PORT` | Puerto MySQL | `3306` |

## Verificación Post-Despliegue

1. **Verificar que el sitio carga**: `https://tu-app.up.railway.app`
2. **Probar archivos estáticos**: CSS e imágenes se cargan correctamente
3. **Probar conexión a BD**: Registrar un usuario, crear un partido
4. **Acceder al admin**: `https://tu-app.up.railway.app/admin/`
5. **Revisar logs**: Railway > Deployments > View logs

## Comandos Útiles de Railway CLI

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Ver logs en tiempo real
railway logs

# Ejecutar comandos
railway run python manage.py migrate
railway run python manage.py createsuperuser

# Abrir shell de Django
railway run python manage.py shell
```

## Solución de Problemas Comunes

### Error: DisallowedHost
- Verifica que `ALLOWED_HOSTS` incluya tu dominio de Railway
- Verifica que `CSRF_TRUSTED_ORIGINS` incluya `https://` completo

### Archivos estáticos no cargan
- Ejecuta `python manage.py collectstatic`
- Verifica que WhiteNoise esté en MIDDLEWARE

### Error de conexión a MySQL
- Verifica las credenciales en variables de entorno
- Asegúrate de usar `${{MYSQL_HOST}}` correcto de Railway
- Verifica que el servicio MySQL esté ejecutándose

### Migraciones no aplicadas
- Ejecuta `railway run python manage.py migrate`
- Verifica que la BD esté accesible

## Dominio Personalizado (Opcional)

1. En Railway > Settings > Domains
2. Agregar dominio personalizado
3. Configurar DNS según instrucciones de Railway
4. Actualizar `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`

## Monitoreo

Railway provee:
- **Logs en tiempo real**: Ver requests y errores
- **Métricas**: CPU, memoria, red
- **Health checks**: Railway reinicia automáticamente si falla

## Backup de Base de Datos

```bash
# Exportar desde Railway
railway run python manage.py dumpdata > backup.json

# Importar
railway run python manage.py loaddata backup.json
```
