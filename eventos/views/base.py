from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from ..models import Localidad, Partido, ParticipantePartido, Usuario


def index(request):
    return render(request, 'index.html')


def home(request):
    partidos = Partido.objects.filter(
        fecha_inicio__gte=timezone.now()
    ).select_related('id_organizador', 'id_localidad').annotate(
        num_participantes=Count('participantes')
    ).order_by('fecha_inicio')[:10]
    return render(request, 'home.html', {'partidos': partidos})


@login_required
def ranking_usuarios(request):
    usuarios = Usuario.objects.filter(is_active=True).order_by('-puntos_friendly')[:50]
    return render(request, 'ranking.html', {'usuarios': usuarios})


def ver_perfil_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    partidos_organizados = Partido.objects.filter(id_organizador=usuario).count()
    partidos_participados = ParticipantePartido.objects.filter(id_usuario=usuario).count()
    return render(request, 'ver_perfil.html', {
        'usuario': usuario,
        'partidos_organizados': partidos_organizados,
        'partidos_participados': partidos_participados,
    })


def lista_localidades():
    return Localidad.objects.all().order_by('nombre')
