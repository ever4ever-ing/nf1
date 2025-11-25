# Sistema de Notificaciones y Perfiles - Instrucciones de Instalación

## 1. Activar el entorno virtual
```powershell
.\venv\Scripts\Activate.ps1
```

## 2. Instalar Pillow para manejo de imágenes
```powershell
pip install Pillow
```

## 3. Crear las tablas en MySQL

### Tabla de Notificaciones
Ejecuta el archivo `create_notificaciones_table.sql`:
```powershell
Get-Content create_notificaciones_table.sql | mysql -u root -p nf1
```

O ejecuta manualmente en MySQL:
```sql
CREATE TABLE IF NOT EXISTS `notificaciones` (
  `id_notificacion` int NOT NULL AUTO_INCREMENT,
  `id_usuario_id` int NOT NULL,
  `id_partido_id` int NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `mensaje` text NOT NULL,
  `leida` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_creacion` datetime(6) NOT NULL,
  `id_usuario_relacionado_id` int DEFAULT NULL,
  `id_mensaje_id` int DEFAULT NULL,
  PRIMARY KEY (`id_notificacion`),
  KEY `notificaciones_id_usuario_id` (`id_usuario_id`),
  KEY `notificaciones_id_partido_id` (`id_partido_id`),
  KEY `notificaciones_fecha_creacion` (`fecha_creacion`),
  CONSTRAINT `notificaciones_id_usuario_fk` FOREIGN KEY (`id_usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `notificaciones_id_partido_fk` FOREIGN KEY (`id_partido_id`) REFERENCES `partidos` (`id_partido`) ON DELETE CASCADE,
  CONSTRAINT `notificaciones_id_usuario_relacionado_fk` FOREIGN KEY (`id_usuario_relacionado_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `notificaciones_id_mensaje_fk` FOREIGN KEY (`id_mensaje_id`) REFERENCES `eventos_mensajepartido` (`id_mensaje`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

### Actualizar tabla de Usuarios
Ejecuta el archivo `update_usuarios_perfil.sql`:
```powershell
Get-Content update_usuarios_perfil.sql | mysql -u root -p nf1
```

O ejecuta manualmente en MySQL:
```sql
ALTER TABLE `usuarios` 
ADD COLUMN `foto_perfil` varchar(100) DEFAULT NULL AFTER `is_admin`,
ADD COLUMN `fecha_nacimiento` date DEFAULT NULL AFTER `foto_perfil`,
ADD COLUMN `hobbies` text DEFAULT NULL AFTER `fecha_nacimiento`,
ADD COLUMN `biografia` text DEFAULT NULL AFTER `hobbies`,
ADD COLUMN `puntos_friendly` int NOT NULL DEFAULT 0 AFTER `biografia`;
```

## 4. Crear las migraciones de Django
```powershell
python manage.py makemigrations
python manage.py migrate --fake
```

## 5. Crear carpeta para archivos media
```powershell
New-Item -Path "media" -ItemType Directory
New-Item -Path "media\perfiles" -ItemType Directory
```

## 6. Iniciar el servidor
```powershell
python manage.py runserver
```

## Características implementadas:

### Sistema de Notificaciones
- ✅ Notificaciones cuando alguien se une a un partido que organizas
- ✅ Notificaciones cuando alguien envía un mensaje en tu partido
- ✅ Notificaciones cuando alguien sale de tu partido
- ✅ Contador en tiempo real en el navbar (actualización cada 30 segundos)
- ✅ Página de notificaciones con filtro de leídas/no leídas
- ✅ Marcar notificaciones como leídas individualmente o todas

### Sistema de Perfiles
- ✅ Foto de perfil (upload de imágenes)
- ✅ Fecha de nacimiento con cálculo automático de edad
- ✅ Hobbies (separados por comas)
- ✅ Biografía personal
- ✅ Vista de perfil propio
- ✅ Vista de perfil de otros usuarios
- ✅ Edición de perfil con preview de foto

### Sistema de Ranking Friendly
- ✅ +10 puntos al unirse a un partido
- ✅ +5 puntos al organizador por cada usuario que se une
- ✅ Página de ranking con top 50 usuarios
- ✅ Indicador de posición (medallas oro/plata/bronce)
- ✅ Badge de puntos en el navbar
- ✅ Estadísticas en el perfil

### Mejoras en la UI
- ✅ Dropdown de usuario en el navbar con foto de perfil
- ✅ Enlaces a perfil y notificaciones desde el menú
- ✅ Link de Ranking en el navbar principal
- ✅ Diseño responsive y moderno con Bootstrap 5

## URLs disponibles:
- `/perfil/` - Mi perfil
- `/perfil/editar/` - Editar perfil
- `/usuario/<id>/` - Ver perfil de otro usuario
- `/ranking/` - Ranking de usuarios
- `/notificaciones/` - Mis notificaciones

