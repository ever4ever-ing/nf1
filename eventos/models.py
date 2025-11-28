from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, apellido, password=None):
        if not email:
            raise ValueError('El usuario debe tener un email')
        
        user = self.model(
            email=self.normalize_email(email),
            nombre=nombre,
            apellido=apellido,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nombre, apellido, password=None):
        user = self.create_user(
            email=email,
            nombre=nombre,
            apellido=apellido,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    # Campos de perfil
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    hobbies = models.TextField(blank=True, null=True, help_text='Hobbies separados por comas')
    biografia = models.TextField(blank=True, null=True)
    
    # Sistema de ranking
    puntos_friendly = models.IntegerField(default=0)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
    
    def get_edad(self):
        """Calcular edad del usuario"""
        if self.fecha_nacimiento:
            from datetime import date
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None
    
    def get_hobbies_list(self):
        """Devolver hobbies como lista"""
        if self.hobbies:
            return [hobby.strip() for hobby in self.hobbies.split(',')]
        return []
    
    def agregar_puntos_participacion(self):
        """Agregar 10 puntos por participar en un partido"""
        self.puntos_friendly += 10
        self.save(update_fields=['puntos_friendly'])
    
    def agregar_puntos_organizador(self, num_participantes):
        """Agregar 5 puntos por cada participante que se une a un partido organizado"""
        self.puntos_friendly += (5 * num_participantes)
        self.save(update_fields=['puntos_friendly'])


class Localidad(models.Model):
    id_localidad = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'localidades'
        verbose_name = 'Localidad'
        verbose_name_plural = 'Localidades'
    
    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    id_reserva = models.BigAutoField(primary_key=True)
    id_cancha = models.ForeignKey('eventos.Cancha', on_delete=models.CASCADE, db_column='id_cancha')
    id_recinto = models.ForeignKey('eventos.Recinto', on_delete=models.CASCADE, db_column='id_recinto')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    fecha_reserva = models.DateTimeField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('confirmada', 'Confirmada'),
            ('cancelada', 'Cancelada'),
            ('completada', 'Completada'),
        ],
        default='confirmada'
    )
    notas = models.TextField(blank=True, null=True, help_text='Observaciones de la reserva')
    
    class Meta:
        db_table = 'reservas'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
    
    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.id_cancha.nombre} - {self.fecha_reserva.date()} {self.hora_inicio}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import datetime, timedelta
        
        # Validar que hora_inicio sea menor que hora_fin
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')
        
        # Calcular duración
        inicio_dt = datetime.combine(self.fecha_reserva.date(), self.hora_inicio)
        fin_dt = datetime.combine(self.fecha_reserva.date(), self.hora_fin)
        duracion = (fin_dt - inicio_dt).total_seconds() / 60
        
        # Validar duración mínima y máxima
        if duracion < 30:
            raise ValidationError('La duración mínima de una reserva es 30 minutos.')
        if duracion > 240:
            raise ValidationError('La duración máxima de una reserva es 4 horas.')
        
        # Verificar que la fecha no sea en el pasado
        from django.utils import timezone
        if self.fecha_reserva.date() < timezone.now().date():
            raise ValidationError('No se pueden hacer reservas para fechas pasadas.')
        
        # Verificar disponibilidad según HorarioCancha
        dia_semana = self.fecha_reserva.weekday()
        horarios_disponibles = HorarioCancha.objects.filter(
            id_cancha=self.id_cancha,
            dia_semana=dia_semana,
            activo=True
        )
        
        if not horarios_disponibles.exists():
            raise ValidationError(f'La cancha no tiene horarios disponibles para {self.fecha_reserva.strftime("%A")}.')
        
        # Verificar que el horario esté dentro de los horarios disponibles
        dentro_horario = False
        for horario in horarios_disponibles:
            if self.hora_inicio >= horario.hora_inicio and self.hora_fin <= horario.hora_fin:
                dentro_horario = True
                break
        
        if not dentro_horario:
            raise ValidationError('El horario seleccionado está fuera de los horarios disponibles de la cancha.')
        
        # Verificar solapamiento con otras reservas confirmadas
        reservas_solapadas = Reserva.objects.filter(
            id_cancha=self.id_cancha,
            fecha_reserva__date=self.fecha_reserva.date(),
            estado='confirmada'
        ).exclude(id_reserva=self.id_reserva)
        
        for reserva in reservas_solapadas:
            if not (self.hora_fin <= reserva.hora_inicio or self.hora_inicio >= reserva.hora_fin):
                raise ValidationError(
                    f'Ya existe una reserva para este horario: {reserva.hora_inicio} - {reserva.hora_fin}'
                )
    
    def duracion_minutos(self):
        """Calcular duración de la reserva en minutos"""
        from datetime import datetime
        inicio_dt = datetime.combine(self.fecha_reserva.date(), self.hora_inicio)
        fin_dt = datetime.combine(self.fecha_reserva.date(), self.hora_fin)
        return int((fin_dt - inicio_dt).total_seconds() / 60)


class Partido(models.Model):
    id_partido = models.AutoField(primary_key=True)
    lugar = models.CharField(max_length=100)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    max_jugadores = models.IntegerField(default=10)
    id_organizador = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_organizador', related_name='partidos_organizados')
    id_localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE, db_column='id_localidad')
    id_reserva = models.ForeignKey(Reserva, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_reserva')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'partidos'
        verbose_name = 'Partido'
        verbose_name_plural = 'Partidos'
    
    def __str__(self):
        return f"Partido {self.id_partido} - {self.lugar}"
    
    def jugadores_actuales(self):
        return self.participantes.count()
    
    def espacios_disponibles(self):
        return self.max_jugadores - self.jugadores_actuales()


class ParticipantePartido(models.Model):
    id_participante = models.AutoField(primary_key=True)
    id_partido = models.ForeignKey(Partido, on_delete=models.CASCADE, db_column='id_partido', related_name='participantes')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario', related_name='partidos_participando')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'participantes_partido'
        verbose_name = 'Participante de Partido'
        verbose_name_plural = 'Participantes de Partidos'
        unique_together = [['id_partido', 'id_usuario']]
    
    def __str__(self):
        return f"{self.id_usuario.nombre} - Partido {self.id_partido.id_partido}"


class MensajePartido(models.Model):
    id_mensaje = models.AutoField(primary_key=True)
    id_partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='mensajes')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_enviados')
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = 'Mensaje de Partido'
        verbose_name_plural = 'Mensajes de Partidos'
    
    def __str__(self):
        return f"{self.id_usuario.nombre} - {self.mensaje[:50]}"


class Notificacion(models.Model):
    TIPOS_NOTIFICACION = [
        ('nuevo_participante', 'Nuevo Participante'),
        ('nuevo_mensaje', 'Nuevo Mensaje'),
        ('salida_participante', 'Salida de Participante'),
    ]
    
    id_notificacion = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    id_partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=50, choices=TIPOS_NOTIFICACION)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Referencias opcionales
    id_usuario_relacionado = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='notificaciones_relacionadas',
        null=True,
        blank=True
    )
    id_mensaje = models.ForeignKey(
        MensajePartido,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'notificaciones'
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
    
    def __str__(self):
        return f"{self.tipo} - {self.id_usuario.nombre} - {'Leída' if self.leida else 'No leída'}"

# ------------------------
# Modelos integrados de canchas
# ------------------------

class Recinto(models.Model):
    id_recinto = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    id_localidad = models.ForeignKey('eventos.Localidad', on_delete=models.CASCADE, db_column='id_localidad')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recintos'
        verbose_name = 'Recinto'
        verbose_name_plural = 'Recintos'

    def __str__(self):
        return f"{self.nombre} - {self.id_localidad.nombre}"


class Cancha(models.Model):
    id_cancha = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    id_recinto = models.ForeignKey(Recinto, on_delete=models.CASCADE, db_column='id_recinto')
    tipo = models.CharField(max_length=50, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'canchas'
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'

    def __str__(self):
        return f"{self.nombre} - {self.id_recinto.nombre}"
    
    def get_horarios_disponibles(self, fecha, duracion_minutos=90):
        """Obtener slots de horarios disponibles para una fecha específica"""
        from datetime import datetime, timedelta
        
        dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
        horarios_cancha = self.horarios.filter(dia_semana=dia_semana, activo=True)
        
        if not horarios_cancha.exists():
            return []
        
        # Obtener reservas existentes para esa fecha
        reservas_existentes = Reserva.objects.filter(
            id_cancha=self,
            fecha_reserva__date=fecha
        ).values_list('hora_inicio', 'hora_fin')
        
        slots_disponibles = []
        for horario in horarios_cancha:
            hora_actual = horario.hora_inicio
            while hora_actual < horario.hora_fin:
                # Calcular hora_fin del slot
                hora_inicio_dt = datetime.combine(fecha, hora_actual)
                hora_fin_dt = hora_inicio_dt + timedelta(minutes=duracion_minutos)
                hora_fin_slot = hora_fin_dt.time()
                
                # Verificar que no exceda el horario de la cancha
                if hora_fin_slot > horario.hora_fin:
                    break
                
                # Verificar que no solape con reservas existentes
                solapa = False
                for res_inicio, res_fin in reservas_existentes:
                    if not (hora_fin_slot <= res_inicio or hora_actual >= res_fin):
                        solapa = True
                        break
                
                if not solapa:
                    slots_disponibles.append({
                        'hora_inicio': hora_actual,
                        'hora_fin': hora_fin_slot,
                        'disponible': True
                    })
                
                # Avanzar en intervalos de 30 minutos
                hora_inicio_dt += timedelta(minutes=30)
                hora_actual = hora_inicio_dt.time()
        
        return slots_disponibles


class HorarioCancha(models.Model):
    """Define los horarios de disponibilidad de una cancha por día de la semana"""
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    id_horario = models.AutoField(primary_key=True)
    id_cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA, help_text='0=Lunes, 6=Domingo')
    hora_inicio = models.TimeField(help_text='Hora de apertura')
    hora_fin = models.TimeField(help_text='Hora de cierre')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'horarios_cancha'
        verbose_name = 'Horario de Cancha'
        verbose_name_plural = 'Horarios de Canchas'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['id_cancha', 'dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.id_cancha.nombre} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')
        
        # Verificar solapamiento con otros horarios de la misma cancha y día
        solapamientos = HorarioCancha.objects.filter(
            id_cancha=self.id_cancha,
            dia_semana=self.dia_semana,
            activo=True
        ).exclude(id_horario=self.id_horario)
        
        for horario in solapamientos:
            if not (self.hora_fin <= horario.hora_inicio or self.hora_inicio >= horario.hora_fin):
                raise ValidationError(f'Este horario solapa con otro horario existente: {horario}')


# ------------------------
# Modelos integrados competitiva
# ------------------------

class Equipo(models.Model):
    id_equipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='equipos/', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    id_anfitrion = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='equipos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    color_primario = models.CharField(max_length=7, default='#007bff', help_text='Color en formato hexadecimal')
    color_secundario = models.CharField(max_length=7, default='#ffffff', help_text='Color en formato hexadecimal')

    class Meta:
        db_table = 'equipos'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'

    def __str__(self):
        return self.nombre

    def contar_miembros(self):
        return self.miembros.count()

    def contar_partidos_jugados(self):
        from django.db import models as djm
        return PartidoCompetitivo.objects.filter(
            djm.Q(id_equipo_local=self) | djm.Q(id_equipo_visitante=self)
        ).count()

    def contar_victorias(self):
        from django.db import models as djm
        return PartidoCompetitivo.objects.filter(
            djm.Q(id_equipo_local=self, goles_local__gt=djm.F('goles_visitante')) |
            djm.Q(id_equipo_visitante=self, goles_visitante__gt=djm.F('goles_local')),
            estado='finalizado'
        ).count()


class MiembroEquipo(models.Model):
    ROLES = [
        ('anfitrion', 'Anfitrión'),
        ('capitan', 'Capitán'),
        ('jugador', 'Jugador'),
    ]
    id_miembro = models.AutoField(primary_key=True)
    id_equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='miembros')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='equipos_miembro')
    rol = models.CharField(max_length=20, choices=ROLES, default='jugador')
    numero_camiseta = models.IntegerField(blank=True, null=True)
    fecha_union = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'miembros_equipo'
        verbose_name = 'Miembro de Equipo'
        verbose_name_plural = 'Miembros de Equipo'
        unique_together = ['id_equipo', 'id_usuario']

    def __str__(self):
        return f"{self.id_usuario.nombre} - {self.id_equipo.nombre} ({self.rol})"


class PartidoCompetitivo(models.Model):
    ESTADOS = [
        ('programado', 'Programado'),
        ('en_curso', 'En Curso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    id_partido = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    id_equipo_local = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_local')
    id_equipo_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='partidos_visitante')
    id_cancha = models.ForeignKey('eventos.Cancha', on_delete=models.SET_NULL, null=True, blank=True)
    id_localidad = models.ForeignKey(Localidad, on_delete=models.SET_NULL, null=True)
    lugar = models.CharField(max_length=200, help_text='Nombre del lugar si no hay cancha registrada')
    fecha_hora = models.DateTimeField()
    goles_local = models.IntegerField(default=0)
    goles_visitante = models.IntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='programado')
    id_creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='partidos_competitivos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'partidos_competitivos'
        verbose_name = 'Partido Competitivo'
        verbose_name_plural = 'Partidos Competitivos'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.id_equipo_local.nombre} vs {self.id_equipo_visitante.nombre}"

    def resultado(self):
        if self.estado != 'finalizado':
            return 'Por jugar'
        return f"{self.goles_local} - {self.goles_visitante}"

    def equipo_ganador(self):
        if self.estado != 'finalizado':
            return None
        if self.goles_local > self.goles_visitante:
            return self.id_equipo_local
        if self.goles_visitante > self.goles_local:
            return self.id_equipo_visitante
        return None


class InvitacionEquipo(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    id_invitacion = models.AutoField(primary_key=True)
    id_equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='invitaciones')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='invitaciones_equipo')
    id_invitador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='invitaciones_enviadas')
    mensaje = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_invitacion = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'invitaciones_equipo'
        verbose_name = 'Invitación a Equipo'
        verbose_name_plural = 'Invitaciones a Equipos'
        unique_together = ['id_equipo', 'id_usuario']
        ordering = ['-fecha_invitacion']

    def __str__(self):
        return f"Invitación a {self.id_usuario.nombre} para {self.id_equipo.nombre}"


class EstadisticaJugador(models.Model):
    id_estadistica = models.AutoField(primary_key=True)
    id_partido = models.ForeignKey(PartidoCompetitivo, on_delete=models.CASCADE, related_name='estadisticas')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='estadisticas_competitivas')
    id_equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    goles = models.IntegerField(default=0)
    asistencias = models.IntegerField(default=0)
    tarjetas_amarillas = models.IntegerField(default=0)
    tarjetas_rojas = models.IntegerField(default=0)

    class Meta:
        db_table = 'estadisticas_jugador'
        verbose_name = 'Estadística de Jugador'
        verbose_name_plural = 'Estadísticas de Jugadores'
        unique_together = ['id_partido', 'id_usuario']

    def __str__(self):
        return f"{self.id_usuario.nombre} - {self.id_partido}"


