from django.db import models

from .partido import Partido
from .usuario import Usuario


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
