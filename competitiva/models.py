from django.db import models
from eventos.models import Usuario, Localidad, Cancha


class Equipo(models.Model):
    """Modelo para equipos competitivos"""
    id_equipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='equipos/', blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    id_anfitrion = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='equipos_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    # Colores del equipo
    color_primario = models.CharField(max_length=7, default='#007bff', help_text='Color en formato hexadecimal')
    color_secundario = models.CharField(max_length=7, default='#ffffff', help_text='Color en formato hexadecimal')
    
    class Meta:
        db_table = 'equipos'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
    
    def __str__(self):
        return self.nombre
    
    def contar_miembros(self):
        """Cuenta el número total de miembros del equipo"""
        return self.miembros.count()
    
    def contar_partidos_jugados(self):
        """Cuenta el número de partidos jugados"""
        return PartidoCompetitivo.objects.filter(
            models.Q(id_equipo_local=self) | models.Q(id_equipo_visitante=self)
        ).count()
    
    def contar_victorias(self):
        """Cuenta el número de victorias del equipo"""
        return PartidoCompetitivo.objects.filter(
            models.Q(id_equipo_local=self, goles_local__gt=models.F('goles_visitante')) |
            models.Q(id_equipo_visitante=self, goles_visitante__gt=models.F('goles_local')),
            estado='finalizado'
        ).count()


class MiembroEquipo(models.Model):
    """Modelo para miembros de equipos"""
    ROLES = [
        ('anfitrion', 'Anfitrión'),
        ('capitan', 'Capitán'),
        ('jugador', 'Jugador'),
    ]
    
    id_miembro = models.AutoField(primary_key=True)
    id_equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='miembros')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='equipos_miembro')
    rol = models.CharField(max_length=20, choices=ROLES, default='jugador')
    numero_camiseta = models.IntegerField(blank=True, null=True)
    fecha_union = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'miembros_equipo'
        verbose_name = 'Miembro de Equipo'
        verbose_name_plural = 'Miembros de Equipo'
        unique_together = ['id_equipo', 'id_usuario']
    
    def __str__(self):
        return f"{self.id_usuario.nombre} - {self.id_equipo.nombre} ({self.rol})"


class PartidoCompetitivo(models.Model):
    """Modelo para partidos competitivos entre equipos"""
    ESTADOS = [
        ('programado', 'Programado'),
        ('en_curso', 'En Curso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    id_partido = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    
    # Equipos
    id_equipo_local = models.ForeignKey(
        Equipo, 
        on_delete=models.CASCADE, 
        related_name='partidos_local'
    )
    id_equipo_visitante = models.ForeignKey(
        Equipo, 
        on_delete=models.CASCADE, 
        related_name='partidos_visitante'
    )
    
    # Ubicación y fecha
    id_cancha = models.ForeignKey(Cancha, on_delete=models.SET_NULL, null=True, blank=True)
    id_localidad = models.ForeignKey(Localidad, on_delete=models.SET_NULL, null=True)
    lugar = models.CharField(max_length=200, help_text='Nombre del lugar si no hay cancha registrada')
    fecha_hora = models.DateTimeField()
    
    # Resultados
    goles_local = models.IntegerField(default=0)
    goles_visitante = models.IntegerField(default=0)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADOS, default='programado')
    
    # Creador del partido
    id_creador = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='partidos_competitivos_creados'
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'partidos_competitivos'
        verbose_name = 'Partido Competitivo'
        verbose_name_plural = 'Partidos Competitivos'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.id_equipo_local.nombre} vs {self.id_equipo_visitante.nombre}"
    
    def resultado(self):
        """Retorna el resultado del partido"""
        if self.estado != 'finalizado':
            return 'Por jugar'
        return f"{self.goles_local} - {self.goles_visitante}"
    
    def equipo_ganador(self):
        """Retorna el equipo ganador o None si hay empate"""
        if self.estado != 'finalizado':
            return None
        if self.goles_local > self.goles_visitante:
            return self.id_equipo_local
        elif self.goles_visitante > self.goles_local:
            return self.id_equipo_visitante
        return None


class InvitacionEquipo(models.Model):
    """Modelo para invitaciones a equipos"""
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    
    id_invitacion = models.AutoField(primary_key=True)
    id_equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='invitaciones')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='invitaciones_equipo')
    id_invitador = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='invitaciones_enviadas'
    )
    mensaje = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_invitacion = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'invitaciones_equipo'
        verbose_name = 'Invitación a Equipo'
        verbose_name_plural = 'Invitaciones a Equipos'
        unique_together = ['id_equipo', 'id_usuario']
        ordering = ['-fecha_invitacion']
    
    def __str__(self):
        return f"Invitación a {self.id_usuario.nombre} para {self.id_equipo.nombre}"


class EstadisticaJugador(models.Model):
    """Modelo para estadísticas de jugadores en partidos"""
    id_estadistica = models.AutoField(primary_key=True)
    id_partido = models.ForeignKey(
        PartidoCompetitivo, 
        on_delete=models.CASCADE, 
        related_name='estadisticas'
    )
    id_usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='estadisticas_competitivas'
    )
    id_equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    
    goles = models.IntegerField(default=0)
    asistencias = models.IntegerField(default=0)
    tarjetas_amarillas = models.IntegerField(default=0)
    tarjetas_rojas = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'estadisticas_jugador'
        verbose_name = 'Estadística de Jugador'
        verbose_name_plural = 'Estadísticas de Jugadores'
        unique_together = ['id_partido', 'id_usuario']
    
    def __str__(self):
        return f"{self.id_usuario.nombre} - {self.id_partido}"

