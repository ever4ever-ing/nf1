from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


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
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    recintos_gestion = models.ManyToManyField(
        'Recinto',
        blank=True,
        related_name='usuarios_admin_recintos',
        verbose_name='Recintos que administra',
        help_text='Recintos gestionables por usuarios del grupo admin_recintos (no aplica a superusuarios).',
    )

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
        return self.nombre_completo

    @property
    def nombre_completo(self):
        n = (self.nombre or '').strip()
        a = (self.apellido or '').strip()
        if n == a:
            return n or (self.email or '')
        parts = [p for p in (n, a) if p]
        return ' '.join(parts) if parts else (self.email or '')

    @property
    def is_staff(self):
        return self.is_admin

    def get_edad(self):
        if self.fecha_nacimiento:
            from datetime import date
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

    def get_hobbies_list(self):
        if self.hobbies:
            return [hobby.strip() for hobby in self.hobbies.split(',')]
        return []

    def agregar_puntos_participacion(self):
        self.puntos_friendly += 10
        self.save(update_fields=['puntos_friendly'])

    def agregar_puntos_organizador(self, num_participantes):
        self.puntos_friendly += (5 * num_participantes)
        self.save(update_fields=['puntos_friendly'])
