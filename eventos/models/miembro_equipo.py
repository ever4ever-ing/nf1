from django.db import models

from .equipo import Equipo
from .usuario import Usuario


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
