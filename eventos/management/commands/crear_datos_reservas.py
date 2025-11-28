from django.core.management.base import BaseCommand
from eventos.models import Localidad, Recinto, Cancha, HorarioCancha
from django.utils import timezone


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el sistema de reservas'

    def handle(self, *args, **kwargs):
        # Crear o obtener localidad
        localidad, created = Localidad.objects.get_or_create(
            nombre='Santiago Centro'
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Localidad creada: {localidad.nombre}'))
        
        # Crear recinto
        recinto, created = Recinto.objects.get_or_create(
            nombre='Complejo Deportivo Central',
            defaults={
                'direccion': 'Av. Libertador Bernardo O\'Higgins 1234',
                'id_localidad': localidad
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Recinto creado: {recinto.nombre}'))
        
        # Crear canchas
        canchas_data = [
            {'nombre': 'Cancha Fútbol 11', 'tipo': 'Pasto natural'},
            {'nombre': 'Cancha Fútbol 7', 'tipo': 'Pasto sintético'},
            {'nombre': 'Cancha Fútbol 5', 'tipo': 'Pasto sintético'},
        ]
        
        for cancha_data in canchas_data:
            cancha, created = Cancha.objects.get_or_create(
                nombre=cancha_data['nombre'],
                id_recinto=recinto,
                defaults={'tipo': cancha_data['tipo']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Cancha creada: {cancha.nombre}'))
                
                # Crear horarios para cada día de lunes a domingo
                for dia in range(7):
                    # Horario mañana
                    HorarioCancha.objects.create(
                        id_cancha=cancha,
                        dia_semana=dia,
                        hora_inicio='09:00',
                        hora_fin='13:00',
                        activo=True
                    )
                    # Horario tarde
                    HorarioCancha.objects.create(
                        id_cancha=cancha,
                        dia_semana=dia,
                        hora_inicio='14:00',
                        hora_fin='18:00',
                        activo=True
                    )
                    # Horario noche
                    HorarioCancha.objects.create(
                        id_cancha=cancha,
                        dia_semana=dia,
                        hora_inicio='18:00',
                        hora_fin='22:00',
                        activo=True
                    )
                
                self.stdout.write(self.style.SUCCESS(f'  Horarios creados para {cancha.nombre}'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Datos de ejemplo creados exitosamente!'))
        self.stdout.write(self.style.SUCCESS('Ahora puedes acceder a /disponibilidad-cancha/ y seleccionar una cancha.'))
