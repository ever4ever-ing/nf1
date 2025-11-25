from django.urls import path
from . import views

app_name = 'competitiva'

urlpatterns = [
    # Equipos
    path('equipos/', views.lista_equipos, name='lista_equipos'),
    path('equipos/crear/', views.crear_equipo, name='crear_equipo'),
    path('equipos/<int:equipo_id>/', views.detalle_equipo, name='detalle_equipo'),
    path('equipos/<int:equipo_id>/editar/', views.editar_equipo, name='editar_equipo'),
    path('equipos/<int:equipo_id>/invitar/', views.invitar_miembro, name='invitar_miembro'),
    path('equipos/<int:equipo_id>/salir/', views.salir_equipo, name='salir_equipo'),
    path('equipos/<int:equipo_id>/crear-partido/', views.crear_partido_competitivo, name='crear_partido_competitivo'),
    path('mis-equipos/', views.mis_equipos, name='mis_equipos'),
    
    # Invitaciones
    path('invitaciones/', views.mis_invitaciones, name='mis_invitaciones'),
    path('invitaciones/<int:invitacion_id>/<str:accion>/', views.responder_invitacion, name='responder_invitacion'),
    
    # Partidos
    path('partidos/', views.lista_partidos_competitivos, name='lista_partidos'),
    path('partidos/<int:partido_id>/', views.detalle_partido_competitivo, name='detalle_partido'),
]
