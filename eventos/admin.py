from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, Localidad, Reserva, Partido, ParticipantePartido, MensajePartido, Notificacion


class UsuarioAdmin(BaseUserAdmin):
    list_display = ('email', 'nombre', 'apellido', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido')}),
        ('Permisos', {'fields': ('is_admin', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('email',)
    filter_horizontal = ()


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ('id_localidad', 'nombre', 'fecha_creacion')
    search_fields = ('nombre',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'id_cancha', 'id_usuario', 'fecha_reserva', 'hora_inicio', 'hora_fin')
    search_fields = ('id_usuario__nombre', 'id_usuario__apellido')
    list_filter = ('fecha_reserva', 'id_cancha')
    date_hierarchy = 'fecha_reserva'


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('id_partido', 'lugar', 'fecha_inicio', 'id_organizador', 'max_jugadores', 'jugadores_actuales', 'espacios_disponibles')
    search_fields = ('lugar', 'descripcion', 'id_organizador__nombre')
    list_filter = ('fecha_inicio', 'id_localidad')
    date_hierarchy = 'fecha_inicio'
    
    def jugadores_actuales(self, obj):
        return obj.jugadores_actuales()
    jugadores_actuales.short_description = 'Jugadores Actuales'
    
    def espacios_disponibles(self, obj):
        return obj.espacios_disponibles()
    espacios_disponibles.short_description = 'Espacios Disponibles'


@admin.register(ParticipantePartido)
class ParticipantePartidoAdmin(admin.ModelAdmin):
    list_display = ('id_participante', 'id_partido', 'id_usuario', 'fecha_registro')
    search_fields = ('id_usuario__nombre', 'id_usuario__apellido')
    list_filter = ('fecha_registro',)


@admin.register(MensajePartido)
class MensajePartidoAdmin(admin.ModelAdmin):
    list_display = ('id_mensaje', 'id_partido', 'id_usuario', 'mensaje_corto', 'fecha_creacion')
    search_fields = ('mensaje', 'id_usuario__nombre', 'id_usuario__apellido')
    list_filter = ('fecha_creacion', 'id_partido')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion',)
    
    def mensaje_corto(self, obj):
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id_notificacion', 'id_usuario', 'tipo', 'id_partido', 'leida', 'fecha_creacion')
    search_fields = ('mensaje', 'id_usuario__nombre', 'id_usuario__apellido')
    list_filter = ('tipo', 'leida', 'fecha_creacion')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion',)
    
    def mensaje_corto(self, obj):
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'


admin.site.register(Usuario, UsuarioAdmin)

