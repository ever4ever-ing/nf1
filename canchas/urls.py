from django.urls import path
from . import views

app_name = 'canchas'

urlpatterns = [
    path('', views.lista_canchas, name='lista_canchas'),
    
    # Recintos (solo admin)
    path('recintos/', views.lista_recintos, name='lista_recintos'),
    path('recintos/crear/', views.crear_recinto, name='crear_recinto'),
    path('recintos/editar/<int:pk>/', views.editar_recinto, name='editar_recinto'),
    
    # Canchas (solo admin)
    path('crear/', views.crear_cancha, name='crear_cancha'),
    path('editar/<int:pk>/', views.editar_cancha, name='editar_cancha'),
]
