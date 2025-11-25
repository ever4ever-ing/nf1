from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from canchas.models import Cancha, Recinto


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
    id_cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, db_column='id_cancha')
    id_recinto = models.ForeignKey(Recinto, on_delete=models.CASCADE, db_column='id_recinto')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    fecha_reserva = models.DateTimeField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reservas'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
    
    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.id_cancha.nombre} - {self.fecha_reserva}"


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

