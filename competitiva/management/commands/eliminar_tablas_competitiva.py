from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Elimina las tablas de la app competitiva'

    def handle(self, *args, **options):
        tablas = [
            'estadisticas_jugador',
            'invitaciones_equipo',
            'partidos_competitivos',
            'miembros_equipo',
            'equipos'
        ]
        
        with connection.cursor() as cursor:
            for tabla in tablas:
                try:
                    self.stdout.write(f'Eliminando tabla {tabla}...')
                    cursor.execute(f'DROP TABLE IF EXISTS {tabla}')
                    self.stdout.write(self.style.SUCCESS(f'✓ Tabla {tabla} eliminada'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'✗ Error eliminando {tabla}: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Tablas eliminadas!'))
