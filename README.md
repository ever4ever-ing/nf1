# Aplicación Django para Eventos Deportivos - NF1

Una aplicación web para registrar eventos deportivos y conectar usuarios en Chile.

## Características

- **Gestión de Usuarios**: Sistema de autenticación personalizado basado en el modelo Usuario de la base de datos
- **Gestión de Partidos**: Crear, ver y unirse a partidos de fútbol
- **Localidades**: Filtrar partidos por localidades de Chile
- **Reservas**: Sistema de reservas de canchas vinculadas a partidos
- **Recintos y Canchas**: Gestión completa de instalaciones deportivas
- **Panel de Administración**: Interface completa para gestionar todos los datos

## Estructura de la Base de Datos

La aplicación utiliza una base de datos MySQL con las siguientes tablas:
- `usuarios`: Usuarios del sistema con autenticación personalizada
- `localidades`: Localidades de Chile (42 ciudades)
- `recintos`: Lugares deportivos
- `canchas`: Canchas específicas dentro de cada recinto
- `reservas`: Reservas de canchas por usuarios
- `partidos`: Eventos deportivos organizados
- `participantes_partido`: Relación entre usuarios y partidos

## Instalación

1. **Crear y activar el entorno virtual** (ya configurado):
   ```bash
   .\venv\Scripts\Activate.ps1
   ```

2. **Instalar dependencias** (ya instaladas):
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar la base de datos MySQL**:
   - Asegúrate de tener MySQL instalado y ejecutándose
   - Actualiza las credenciales en `config/settings.py` si es necesario:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'nf1',
             'USER': 'root',
             'PASSWORD': '',  # Ajusta tu contraseña
             'HOST': 'localhost',
             'PORT': '3306',
         }
     }
     ```

4. **Crear la base de datos y ejecutar el script SQL**:
   ```bash
   mysql -u root -p < nf1.sql
   ```

5. **Ejecutar migraciones de Django** (sin crear nuevas tablas, solo sincronizar):
   ```bash
   python manage.py migrate --run-syncdb
   ```

6. **Crear un superusuario** (debe hacerse desde la base de datos o el admin después):
   ```bash
   python manage.py createsuperuser
   ```

7. **Ejecutar el servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```

8. **Acceder a la aplicación**:
   - Página principal: http://localhost:8000/
   - Panel de administración: http://localhost:8000/admin/

## Uso

### Para Usuarios
- **Ver partidos**: Navega por los partidos disponibles en la página principal
- **Filtrar por localidad**: Usa el filtro en la lista de partidos
- **Unirse a un partido**: Haz clic en "Unirse al Partido" (requiere login)
- **Ver mis partidos**: Accede a tu perfil para ver los partidos que organizas o en los que participas

### Para Administradores
Accede al panel de administración para:
- Crear y gestionar usuarios
- Agregar localidades, recintos y canchas
- Crear reservas
- Organizar partidos
- Gestionar participantes

## Modelos Principales

- **Usuario**: Modelo personalizado con email como identificador único
- **Partido**: Evento deportivo con organizador, localidad, y límite de jugadores
- **ParticipantePartido**: Relación entre usuarios y partidos
- **Reserva**: Reserva de cancha con fecha, hora de inicio y fin

## Tecnologías Utilizadas

- Django 5.2.8
- MySQL
- mysqlclient
- Python 3.13

## Estructura del Proyecto

```
nf1/
├── config/              # Configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── eventos/             # Aplicación principal
│   ├── models.py       # Modelos de la base de datos
│   ├── views.py        # Vistas y lógica
│   ├── urls.py         # URLs de la aplicación
│   ├── admin.py        # Configuración del admin
│   └── templates/      # Plantillas HTML
├── manage.py
├── nf1.sql             # Script de la base de datos
└── requirements.txt    # Dependencias
```

## Próximos Pasos

- Implementar sistema de autenticación frontend (login/registro)
- Agregar formularios para crear partidos desde la interfaz web
- Implementar sistema de notificaciones
- Agregar búsqueda avanzada de partidos
- Crear API REST para aplicación móvil

## Despliegue en Producción

### Railway (Recomendado)

Para desplegar en Railway, sigue la guía completa en [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md).

**Resumen rápido:**

1. **Preparar el proyecto** (ya está listo):
   - ✅ `Procfile` configurado con Gunicorn
   - ✅ `requirements.txt` con dependencias de producción
   - ✅ `runtime.txt` especifica Python 3.13.9
   - ✅ WhiteNoise para archivos estáticos

2. **Crear proyecto en Railway**:
   ```bash
   # Opción 1: Desde GitHub
   - Conecta tu repositorio en railway.app
   - Railway detectará automáticamente Django
   
   # Opción 2: Railway CLI
   npm i -g @railway/cli
   railway login
   railway init
   railway up
   ```

3. **Agregar servicio MySQL**:
   - En Railway dashboard: New > Database > MySQL
   - Railway generará las credenciales automáticamente

4. **Configurar variables de entorno**:
   ```bash
   SECRET_KEY=tu-clave-secreta-generada
   DEBUG=False
   ALLOWED_HOSTS=tu-app.up.railway.app
   CSRF_TRUSTED_ORIGINS=https://tu-app.up.railway.app
   
   # Variables de MySQL (usar referencias de Railway)
   DB_NAME=${{MYSQL_DATABASE}}
   DB_USER=${{MYSQL_USER}}
   DB_PASSWORD=${{MYSQL_PASSWORD}}
   DB_HOST=${{MYSQL_HOST}}
   DB_PORT=${{MYSQL_PORT}}
   ```

5. **Aplicar migraciones**:
   ```bash
   railway run python manage.py migrate
   railway run python manage.py createsuperuser
   railway run python manage.py loaddata eventos/fixtures/localidades.json
   ```

6. **Verificar despliegue**:
   - Visita `https://tu-app.up.railway.app`
   - Prueba login y funcionalidades principales
   - Accede al admin: `https://tu-app.up.railway.app/admin`

### Otras Plataformas

**Render:**
- Similar a Railway, usa `Procfile` y variables de entorno
- Agrega `build.sh` para automatizar migraciones

**Heroku:**
- Compatible con la configuración actual
- Usa `Procfile` existente
- Configura PostgreSQL o MySQL como add-on

**VPS (DigitalOcean, AWS EC2, etc.):**
- Instala Python 3.13, MySQL, Nginx
- Configura Gunicorn como servicio systemd
- Usa Nginx como proxy inverso
- Configura SSL con Let's Encrypt

### Variables de Entorno Necesarias

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Django | Genera con `get_random_secret_key()` |
| `DEBUG` | Modo debug | `False` en producción |
| `ALLOWED_HOSTS` | Dominios permitidos | `app.railway.app,midominio.com` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes CSRF | `https://app.railway.app` |
| `DB_NAME` | Nombre BD | `railway` o `nf1` |
| `DB_USER` | Usuario BD | `root` |
| `DB_PASSWORD` | Password BD | Tu contraseña segura |
| `DB_HOST` | Host BD | `localhost` o host remoto |
| `DB_PORT` | Puerto BD | `3306` |

### Comandos de Mantenimiento

```bash
# Ver logs en tiempo real (Railway)
railway logs

# Ejecutar migraciones
railway run python manage.py migrate

# Crear backup de base de datos
railway run python manage.py dumpdata > backup.json

# Cargar datos
railway run python manage.py loaddata backup.json

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

## Licencia

Este proyecto es para uso educativo en el programa Talento Digital.
