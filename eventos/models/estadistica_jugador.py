from django.db import models

from .equipo import Equipo
from .partido_competitivo import PartidoCompetitivo
from .usuario import Usuario


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
