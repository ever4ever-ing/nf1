from django.core.management.base import BaseCommand
from django.db import connection
import os


class Command(BaseCommand):
    help = 'Crea las tablas de la app competitiva ejecutando el SQL directamente'

    def handle(self, *args, **options):
        sql_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'create_competitiva_tables.sql')
        
        self.stdout.write(f'Leyendo SQL desde: {sql_file}')
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Separar las sentencias SQL por punto y coma
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        with connection.cursor() as cursor:
            for i, statement in enumerate(sql_statements, 1):
                try:
                    self.stdout.write(f'\nEjecutando sentencia {i}...')
                    cursor.execute(statement)
                    self.stdout.write(self.style.SUCCESS(f'✓ Sentencia {i} ejecutada correctamente'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'✗ Error en sentencia {i}: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Tablas creadas exitosamente!'))
        self.stdout.write('\nAhora ejecuta: python manage.py migrate competitiva --fake')
