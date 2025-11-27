from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('partidos/', views.lista_partidos, name='lista_partidos'),
    path('partidos/crear/', views.crear_partido, name='crear_partido'),
    path('partidos/<int:partido_id>/', views.detalle_partido, name='detalle_partido'),
    path('partidos/<int:partido_id>/editar/', views.editar_partido, name='editar_partido'),
    path('partidos/<int:partido_id>/cancelar/', views.cancelar_partido, name='cancelar_partido'),
    path('partidos/<int:partido_id>/unirse/', views.unirse_partido, name='unirse_partido'),
    path('partidos/<int:partido_id>/salir/', views.salir_partido, name='salir_partido'),
    path('mis-partidos/', views.mis_partidos, name='mis_partidos'),
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('notificaciones/', views.mis_notificaciones, name='mis_notificaciones'),
    path('notificaciones/<int:notificacion_id>/marcar-leida/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('api/notificaciones/nuevas/', views.obtener_notificaciones_nuevas, name='obtener_notificaciones_nuevas'),
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('usuario/<int:usuario_id>/', views.ver_perfil_usuario, name='ver_perfil_usuario'),
    path('ranking/', views.ranking_usuarios, name='ranking_usuarios'),
]
