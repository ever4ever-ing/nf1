from django.db import models


class Recinto(models.Model):
    id_recinto = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    id_localidad = models.ForeignKey('eventos.Localidad', on_delete=models.CASCADE, db_column='id_localidad')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recintos'
        verbose_name = 'Recinto'
        verbose_name_plural = 'Recintos'

    def __str__(self):
        return f"{self.nombre} - {self.id_localidad.nombre}"
