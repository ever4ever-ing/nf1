from django.db import models

from .mensaje_partido import MensajePartido
from .partido import Partido
from .usuario import Usuario


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
