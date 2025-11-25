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


class Cancha(models.Model):
    id_cancha = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    id_recinto = models.ForeignKey(Recinto, on_delete=models.CASCADE, db_column='id_recinto')
    tipo = models.CharField(max_length=50, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'canchas'
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'
    
    def __str__(self):
        return f"{self.nombre} - {self.id_recinto.nombre}"
