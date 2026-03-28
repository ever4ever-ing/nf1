from django.db import models

from .recinto import Recinto


class Cancha(models.Model):
    id_cancha = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    id_recinto = models.ForeignKey(Recinto, on_delete=models.CASCADE, db_column='id_recinto')
    tipo = models.CharField(max_length=50, null=True, blank=True)
    max_jugadores = models.PositiveSmallIntegerField(
        default=10,
        help_text='Cupo máximo de jugadores para partidos en esta cancha.',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'canchas'
        verbose_name = 'Cancha'
        verbose_name_plural = 'Canchas'

    def __str__(self):
        return f"{self.nombre} - {self.id_recinto.nombre}"

    def get_horarios_disponibles(self, fecha, duracion_minutos=90):
        from datetime import datetime, timedelta
        from .reserva import Reserva

        dia_semana = fecha.weekday()
        horarios_cancha = self.horarios.filter(dia_semana=dia_semana, activo=True)

        if not horarios_cancha.exists():
            return []

        reservas_existentes = Reserva.objects.filter(
            id_cancha=self,
            fecha_reserva=fecha
        ).values_list('hora_inicio', 'hora_fin')

        slots_disponibles = []
        for horario in horarios_cancha:
            hora_actual = horario.hora_inicio
            while hora_actual < horario.hora_fin:
                hora_inicio_dt = datetime.combine(fecha, hora_actual)
                hora_fin_dt = hora_inicio_dt + timedelta(minutes=duracion_minutos)
                hora_fin_slot = hora_fin_dt.time()

                if hora_fin_slot > horario.hora_fin:
                    break

                solapa = False
                for res_inicio, res_fin in reservas_existentes:
                    if not (hora_fin_slot <= res_inicio or hora_actual >= res_fin):
                        solapa = True
                        break

                if not solapa:
                    slots_disponibles.append({
                        'hora_inicio': hora_actual,
                        'hora_fin': hora_fin_slot,
                        'disponible': True
                    })

                hora_inicio_dt += timedelta(minutes=30)
                hora_actual = hora_inicio_dt.time()

        return slots_disponibles
