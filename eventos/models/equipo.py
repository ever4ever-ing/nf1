from django.db import models

from .usuario import Usuario


class Equipo(models.Model):
    id_equipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='equipos/', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    id_anfitrion = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='equipos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    color_primario = models.CharField(max_length=7, default='#007bff', help_text='Color en formato hexadecimal')
    color_secundario = models.CharField(max_length=7, default='#ffffff', help_text='Color en formato hexadecimal')

    class Meta:
        db_table = 'equipos'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'

    def __str__(self):
        return self.nombre

    def contar_miembros(self):
        return self.miembros.count()

    def contar_partidos_jugados(self):
        from django.db import models as djm
        from .partido_competitivo import PartidoCompetitivo
        return PartidoCompetitivo.objects.filter(
            djm.Q(id_equipo_local=self) | djm.Q(id_equipo_visitante=self)
        ).count()

    def contar_victorias(self):
        from django.db import models as djm
        from .partido_competitivo import PartidoCompetitivo
        return PartidoCompetitivo.objects.filter(
            djm.Q(id_equipo_local=self, goles_local__gt=djm.F('goles_visitante')) |
            djm.Q(id_equipo_visitante=self, goles_visitante__gt=djm.F('goles_local')),
            estado='finalizado'
        ).count()
