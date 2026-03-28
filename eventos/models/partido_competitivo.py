from django.db import models

from .equipo import Equipo
from .localidad import Localidad
from .usuario import Usuario


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
