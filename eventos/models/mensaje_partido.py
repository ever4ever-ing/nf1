from django.db import models

from .partido import Partido
from .usuario import Usuario


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
