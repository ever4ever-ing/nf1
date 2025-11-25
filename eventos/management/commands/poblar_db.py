"""
Script para poblar la base de datos con datos iniciales
Ejecutar con: python manage.py shell < eventos/management/commands/poblar_db.py
O mejor: python manage.py poblar_db
"""
from django.core.management.base import BaseCommand
from eventos.models import Localidad, Usuario, Recinto, Cancha, Partido
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando población de la base de datos...')
        
        # 1. Crear localidades
        self.stdout.write('Creando localidades...')
        localidades_data = [
            'Arica', 'Iquique', 'Antofagasta', 'Copiapó', 'La Serena',
            'Valparaíso', 'Santiago', 'Rancagua', 'Talca', 'Chillán',
            'Concepción', 'Temuco', 'Valdivia', 'Puerto Montt', 'Coyhaique',
            'Punta Arenas', 'Calama', 'Quillota', 'San Antonio', 'Melipilla',
            'Curicó', 'Los Ángeles', 'Osorno', 'Puerto Varas', 'Castro',
            'Ancud', 'Vallenar', 'Ovalle', 'San Fernando', 'Linares',
            'Coronel', 'Talcahuano', 'Lota', 'Angol', 'Villarrica',
            'Pucón', 'La Unión', 'Río Bueno', 'Quellón', 'Aysén',
            'Porvenir', 'Natales'
        ]
        
        localidades_creadas = 0
        for nombre in localidades_data:
            localidad, created = Localidad.objects.get_or_create(nombre=nombre)
            if created:
                localidades_creadas += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {localidades_creadas} localidades creadas'))
        
        # 2. Crear usuarios de ejemplo
        self.stdout.write('Creando usuarios de ejemplo...')
        usuarios_data = [
            {'nombre': 'Juan', 'apellido': 'Pérez', 'email': 'juan@example.com'},
            {'nombre': 'María', 'apellido': 'González', 'email': 'maria@example.com'},
            {'nombre': 'Carlos', 'apellido': 'Rodríguez', 'email': 'carlos@example.com'},
            {'nombre': 'Ana', 'apellido': 'Martínez', 'email': 'ana@example.com'},
            {'nombre': 'Luis', 'apellido': 'López', 'email': 'luis@example.com'},
        ]
        
        usuarios_creados = 0
        usuarios = []
        for data in usuarios_data:
            try:
                usuario = Usuario.objects.create_user(
                    email=data['email'],
                    nombre=data['nombre'],
                    apellido=data['apellido'],
                    password='password123'
                )
                usuarios.append(usuario)
                usuarios_creados += 1
            except:
                usuario = Usuario.objects.get(email=data['email'])
                usuarios.append(usuario)
        
        self.stdout.write(self.style.SUCCESS(f'✓ {usuarios_creados} usuarios creados'))
        
        # 3. Crear recintos de ejemplo
        self.stdout.write('Creando recintos de ejemplo...')
        santiago = Localidad.objects.get(nombre='Santiago')
        valparaiso = Localidad.objects.get(nombre='Valparaíso')
        concepcion = Localidad.objects.get(nombre='Concepción')
        
        recintos_data = [
            {'nombre': 'Estadio Nacional', 'direccion': 'Av. Grecia 2001, Santiago', 'localidad': santiago},
            {'nombre': 'Complejo Deportivo Municipal', 'direccion': 'Av. Vicuña Mackenna 7500, Santiago', 'localidad': santiago},
            {'nombre': 'Cancha El Sporting', 'direccion': 'Calle Los Carrera 123, Valparaíso', 'localidad': valparaiso},
            {'nombre': 'Arena Deportiva', 'direccion': 'Av. Libertador 456, Concepción', 'localidad': concepcion},
        ]
        
        recintos_creados = 0
        recintos = []
        for data in recintos_data:
            recinto, created = Recinto.objects.get_or_create(
                nombre=data['nombre'],
                defaults={'direccion': data['direccion'], 'id_localidad': data['localidad']}
            )
            recintos.append(recinto)
            if created:
                recintos_creados += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {recintos_creados} recintos creados'))
        
        # 4. Crear canchas
        self.stdout.write('Creando canchas...')
        canchas_creadas = 0
        canchas = []
        for recinto in recintos:
            for i in range(1, 4):
                cancha, created = Cancha.objects.get_or_create(
                    nombre=f'Cancha {i}',
                    id_recinto=recinto,
                    defaults={'tipo': 'Fútbol 7' if i % 2 else 'Fútbol 11'}
                )
                canchas.append(cancha)
                if created:
                    canchas_creadas += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {canchas_creadas} canchas creadas'))
        
        # 5. Crear partidos de ejemplo
        self.stdout.write('Creando partidos de ejemplo...')
        partidos_creados = 0
        
        if usuarios:
            partidos_data = [
                {
                    'lugar': 'Estadio Nacional - Santiago',
                    'fecha_inicio': timezone.now() + timedelta(days=2),
                    'descripcion': 'Partido amistoso de fútbol 7. Todos los niveles bienvenidos.',
                    'max_jugadores': 14,
                    'organizador': usuarios[0],
                    'localidad': santiago
                },
                {
                    'lugar': 'Complejo Municipal - Santiago',
                    'fecha_inicio': timezone.now() + timedelta(days=5),
                    'descripcion': 'Pichanga de fin de semana. Ven y juega!',
                    'max_jugadores': 10,
                    'organizador': usuarios[1],
                    'localidad': santiago
                },
                {
                    'lugar': 'Cancha El Sporting - Valparaíso',
                    'fecha_inicio': timezone.now() + timedelta(days=7),
                    'descripcion': 'Partido de fútbol 11. Buscamos jugadores para completar equipos.',
                    'max_jugadores': 22,
                    'organizador': usuarios[2],
                    'localidad': valparaiso
                },
                {
                    'lugar': 'Arena Deportiva - Concepción',
                    'fecha_inicio': timezone.now() + timedelta(days=3),
                    'descripcion': 'Torneo relámpago. Inscripciones abiertas.',
                    'max_jugadores': 16,
                    'organizador': usuarios[3],
                    'localidad': concepcion
                },
            ]
            
            for data in partidos_data:
                partido, created = Partido.objects.get_or_create(
                    lugar=data['lugar'],
                    defaults={
                        'fecha_inicio': data['fecha_inicio'],
                        'descripcion': data['descripcion'],
                        'max_jugadores': data['max_jugadores'],
                        'id_organizador': data['organizador'],
                        'id_localidad': data['localidad']
                    }
                )
                if created:
                    partidos_creados += 1
            
            self.stdout.write(self.style.SUCCESS(f'✓ {partidos_creados} partidos creados'))
        
        self.stdout.write(self.style.SUCCESS('\n¡Base de datos poblada exitosamente!'))
        self.stdout.write(f'Total:')
        self.stdout.write(f'  - Localidades: {Localidad.objects.count()}')
        self.stdout.write(f'  - Usuarios: {Usuario.objects.count()}')
        self.stdout.write(f'  - Recintos: {Recinto.objects.count()}')
        self.stdout.write(f'  - Canchas: {Cancha.objects.count()}')
        self.stdout.write(f'  - Partidos: {Partido.objects.count()}')
