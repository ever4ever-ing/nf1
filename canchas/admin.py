from django.contrib import admin
from .models import Recinto, Cancha


@admin.register(Recinto)
class RecintoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id_localidad', 'direccion', 'fecha_creacion']
    list_filter = ['id_localidad']
    search_fields = ['nombre', 'direccion']


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'id_recinto', 'tipo', 'fecha_creacion']
    list_filter = ['tipo', 'id_recinto__id_localidad']
    search_fields = ['nombre', 'id_recinto__nombre']
