from django.db import models


class HorarioCancha(models.Model):
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    id_horario = models.AutoField(primary_key=True)
    id_cancha = models.ForeignKey('eventos.Cancha', on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS_SEMANA, help_text='0=Lunes, 6=Domingo')
    hora_inicio = models.TimeField(help_text='Hora de apertura')
    hora_fin = models.TimeField(help_text='Hora de cierre')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'horarios_cancha'
        verbose_name = 'Horario de Cancha'
        verbose_name_plural = 'Horarios de Canchas'
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['id_cancha', 'dia_semana', 'hora_inicio']

    def __str__(self):
        if self.id_cancha_id is None:
            return f"Horario (sin cancha) - {self.get_dia_semana_display()}"
        return f"{self.id_cancha.nombre} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')
        if self.id_cancha_id is None:
            return

        solapamientos = HorarioCancha.objects.filter(
            id_cancha=self.id_cancha,
            dia_semana=self.dia_semana,
            activo=True
        ).exclude(id_horario=self.id_horario)

        for horario in solapamientos:
            if not (self.hora_fin <= horario.hora_inicio or self.hora_inicio >= horario.hora_fin):
                raise ValidationError(f'Este horario solapa con otro horario existente: {horario}')
