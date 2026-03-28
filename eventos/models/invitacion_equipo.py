from django.db import models

from .equipo import Equipo
from .usuario import Usuario


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
