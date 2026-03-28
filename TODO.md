# TODO - NF1

## Prioridad alta (esta semana)

- [ ] Endurecer autenticacion y permisos del modelo `Usuario`
  - [ ] Reemplazar `has_perm()` y `has_module_perms()` que hoy retornan `True`
  - [ ] Evaluar migrar a `PermissionsMixin`
  - [ ] Verificar accesos en admin y vistas protegidas

- [ ] Asegurar configuracion de produccion en `config/settings.py`
  - [ ] Eliminar fallback inseguro de `SECRET_KEY`
  - [ ] Evitar `DEBUG=True` por defecto en entornos no locales
  - [ ] Revisar `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` por variables de entorno

- [ ] Normalizar tipos de `Notificacion`
  - [ ] Definir catalogo unico de tipos (`nuevo_participante`, `nuevo_mensaje`, etc.)
  - [ ] Alinear `models.py` y `views.py` para evitar tipos no declarados (`info`, `cancelacion`)
  - [ ] Validar comportamiento en templates de notificaciones

## Prioridad media

- [ ] Corregir manejo de perfil de usuario
  - [ ] Agregar campo `telefono` al modelo `Usuario` y crear migracion, o
  - [ ] Remover su uso en `editar_perfil` si no se va a persistir

- [ ] Ajustar configuracion de media/static
  - [ ] Cambiar `MEDIA_URL` a `'/media/'`
  - [ ] Probar carga de imagenes en local y en Railway

- [ ] Definir estrategia unica de MySQL
  - [ ] Confirmar si se usara `mysqlclient` o `pymysql`
  - [ ] Alinear `requirements.txt` y documentacion

## Prioridad baja / mantenimiento

- [ ] Mejorar cobertura de pruebas
  - [ ] Validaciones de reservas (solapamientos, duracion, horarios)
  - [ ] Flujos de partidos (crear, unirse, salir, cancelar)
  - [ ] Flujos de competitiva (invitaciones, equipos, partidos)

- [ ] Mejorar higiene del repositorio
  - [ ] Mantener `.gitignore` actualizado
  - [ ] Evitar artefactos locales (`venv`, `__pycache__`, logs) en cambios futuros

- [ ] Documentacion tecnica
  - [ ] Agregar checklist de despliegue seguro
  - [ ] Documentar variables de entorno obligatorias y opcionales

## Backlog (ideas)

- [ ] API REST para clientes moviles
- [ ] Notificaciones en tiempo real (polling mejorado o websockets)
- [ ] Busqueda avanzada y filtros de partidos
- [ ] Panel de metricas para actividad de usuarios y canchas
