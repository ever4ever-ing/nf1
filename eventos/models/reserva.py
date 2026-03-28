from django.db import models

from .usuario import Usuario


class Reserva(models.Model):
    id_reserva = models.BigAutoField(primary_key=True)
    id_cancha = models.ForeignKey('eventos.Cancha', on_delete=models.CASCADE, db_column='id_cancha')
    id_recinto = models.ForeignKey('eventos.Recinto', on_delete=models.CASCADE, db_column='id_recinto')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('confirmada', 'Confirmada'),
            ('cancelada', 'Cancelada'),
            ('completada', 'Completada'),
        ],
        default='confirmada'
    )
    notas = models.TextField(blank=True, null=True, help_text='Observaciones de la reserva')

    class Meta:
        db_table = 'reservas'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.id_cancha.nombre} - {self.fecha_reserva} {self.hora_inicio}"

    def clean(self):
        from datetime import datetime
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        from .horario_cancha import HorarioCancha

        if self.hora_inicio >= self.hora_fin:
            raise ValidationError('La hora de inicio debe ser anterior a la hora de fin.')

        inicio_dt = datetime.combine(self.fecha_reserva, self.hora_inicio)
        fin_dt = datetime.combine(self.fecha_reserva, self.hora_fin)
        duracion = (fin_dt - inicio_dt).total_seconds() / 60

        if duracion < 30:
            raise ValidationError('La duración mínima de una reserva es 30 minutos.')
        if duracion > 240:
            raise ValidationError('La duración máxima de una reserva es 4 horas.')

        if self.fecha_reserva < timezone.now().date():
            raise ValidationError('No se pueden hacer reservas para fechas pasadas.')

        dia_semana = self.fecha_reserva.weekday()
        horarios_disponibles = HorarioCancha.objects.filter(
            id_cancha=self.id_cancha,
            dia_semana=dia_semana,
            activo=True
        )

        if not horarios_disponibles.exists():
            raise ValidationError(f'La cancha no tiene horarios disponibles para {self.fecha_reserva.strftime("%A")}.')

        dentro_horario = False
        for horario in horarios_disponibles:
            if self.hora_inicio >= horario.hora_inicio and self.hora_fin <= horario.hora_fin:
                dentro_horario = True
                break

        if not dentro_horario:
            raise ValidationError('El horario seleccionado está fuera de los horarios disponibles de la cancha.')

        reservas_solapadas = self.__class__.objects.filter(
            id_cancha=self.id_cancha,
            fecha_reserva=self.fecha_reserva,
            estado='confirmada'
        ).exclude(id_reserva=self.id_reserva)

        for reserva in reservas_solapadas:
            if not (self.hora_fin <= reserva.hora_inicio or self.hora_inicio >= reserva.hora_fin):
                raise ValidationError(
                    f'Ya existe una reserva para este horario: {reserva.hora_inicio} - {reserva.hora_fin}'
                )

    def duracion_minutos(self):
        from datetime import datetime
        inicio_dt = datetime.combine(self.fecha_reserva, self.hora_inicio)
        fin_dt = datetime.combine(self.fecha_reserva, self.hora_fin)
        return int((fin_dt - inicio_dt).total_seconds() / 60)
