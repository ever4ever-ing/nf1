from django.db import models

from .localidad import Localidad
from .reserva import Reserva
from .usuario import Usuario


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
