from django.contrib import admin
from .models import Equipo, MiembroEquipo, PartidoCompetitivo, InvitacionEquipo, EstadisticaJugador


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('id_equipo', 'nombre', 'id_anfitrion', 'contar_miembros', 'activo', 'fecha_creacion')
    search_fields = ('nombre', 'id_anfitrion__nombre', 'id_anfitrion__apellido')
    list_filter = ('activo', 'fecha_creacion')
    date_hierarchy = 'fecha_creacion'


@admin.register(MiembroEquipo)
class MiembroEquipoAdmin(admin.ModelAdmin):
    list_display = ('id_miembro', 'id_equipo', 'id_usuario', 'rol', 'numero_camiseta', 'activo', 'fecha_union')
    search_fields = ('id_equipo__nombre', 'id_usuario__nombre', 'id_usuario__apellido')
    list_filter = ('rol', 'activo', 'fecha_union')


@admin.register(PartidoCompetitivo)
class PartidoCompetitivoAdmin(admin.ModelAdmin):
    list_display = ('id_partido', 'nombre', 'id_equipo_local', 'id_equipo_visitante', 'resultado', 'estado', 'fecha_hora')
    search_fields = ('nombre', 'id_equipo_local__nombre', 'id_equipo_visitante__nombre')
    list_filter = ('estado', 'fecha_hora', 'id_localidad')
    date_hierarchy = 'fecha_hora'


@admin.register(InvitacionEquipo)
class InvitacionEquipoAdmin(admin.ModelAdmin):
    list_display = ('id_invitacion', 'id_equipo', 'id_usuario', 'id_invitador', 'estado', 'fecha_invitacion')
    search_fields = ('id_equipo__nombre', 'id_usuario__nombre', 'id_usuario__apellido')
    list_filter = ('estado', 'fecha_invitacion')
    date_hierarchy = 'fecha_invitacion'


@admin.register(EstadisticaJugador)
class EstadisticaJugadorAdmin(admin.ModelAdmin):
    list_display = ('id_estadistica', 'id_partido', 'id_usuario', 'id_equipo', 'goles', 'asistencias', 'tarjetas_amarillas', 'tarjetas_rojas')
    search_fields = ('id_usuario__nombre', 'id_usuario__apellido', 'id_partido__nombre')
    list_filter = ('id_equipo',)

