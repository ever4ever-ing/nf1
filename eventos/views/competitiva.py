from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q as DJQ
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import EquipoForm, PartidoCompetitivoForm
from ..models import Equipo, InvitacionEquipo, MiembroEquipo, PartidoCompetitivo, Usuario


def lista_equipos(request):
    equipos = Equipo.objects.filter(activo=True).annotate(num_miembros=Count('miembros')).order_by('-fecha_creacion')
    return render(request, 'competitiva/lista_equipos.html', {'equipos': equipos})


def detalle_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo.objects.prefetch_related('miembros__id_usuario'), id_equipo=equipo_id)
    miembros = equipo.miembros.filter(activo=True).select_related('id_usuario')
    partidos = PartidoCompetitivo.objects.filter(
        DJQ(id_equipo_local=equipo) | DJQ(id_equipo_visitante=equipo)
    ).select_related('id_equipo_local', 'id_equipo_visitante').order_by('-fecha_hora')[:10]
    es_miembro = False
    es_anfitrion = False
    invitacion_pendiente = None
    if request.user.is_authenticated:
        es_miembro = miembros.filter(id_usuario=request.user).exists()
        es_anfitrion = equipo.id_anfitrion == request.user
        invitacion_pendiente = InvitacionEquipo.objects.filter(
            id_equipo=equipo, id_usuario=request.user, estado='pendiente'
        ).first()
    return render(request, 'competitiva/detalle_equipo.html', {
        'equipo': equipo,
        'miembros': miembros,
        'partidos': partidos,
        'es_miembro': es_miembro,
        'es_anfitrion': es_anfitrion,
        'invitacion_pendiente': invitacion_pendiente,
    })


@login_required
def crear_equipo(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save(commit=False)
            equipo.id_anfitrion = request.user
            equipo.save()
            MiembroEquipo.objects.create(id_equipo=equipo, id_usuario=request.user, rol='anfitrion')
            messages.success(request, f'Equipo "{equipo.nombre}" creado.')
            return redirect('competitiva_detalle_equipo', equipo_id=equipo.id_equipo)
    else:
        form = EquipoForm()
    return render(request, 'competitiva/crear_equipo.html', {'form': form})


@login_required
def editar_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    if equipo.id_anfitrion != request.user:
        messages.error(request, 'No tienes permiso para editar este equipo.')
        return redirect('competitiva_detalle_equipo', equipo_id=equipo_id)
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo actualizado.')
            return redirect('competitiva_detalle_equipo', equipo_id=equipo_id)
    else:
        form = EquipoForm(instance=equipo)
    return render(request, 'competitiva/editar_equipo.html', {'form': form, 'equipo': equipo})


@login_required
def invitar_miembro(request, equipo_id):
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    miembro = MiembroEquipo.objects.filter(
        id_equipo=equipo, id_usuario=request.user, rol__in=['anfitrion', 'capitan']
    ).first()
    if not miembro:
        messages.error(request, 'No tienes permiso para invitar miembros.')
        return redirect('competitiva_detalle_equipo', equipo_id=equipo_id)
    if request.method == 'POST':
        usuario_id = request.POST.get('id_usuario')
        mensaje_texto = request.POST.get('mensaje', '')
        usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
        if MiembroEquipo.objects.filter(id_equipo=equipo, id_usuario=usuario).exists():
            messages.warning(request, 'Este usuario ya es miembro.')
            return redirect('competitiva_detalle_equipo', equipo_id=equipo_id)
        InvitacionEquipo.objects.get_or_create(
            id_equipo=equipo,
            id_usuario=usuario,
            defaults={'id_invitador': request.user, 'mensaje': mensaje_texto}
        )
        messages.success(request, f'Invitación enviada a {usuario.nombre}.')
        return redirect('competitiva_detalle_equipo', equipo_id=equipo_id)
    miembros_ids = equipo.miembros.values_list('id_usuario', flat=True)
    usuarios_disponibles = Usuario.objects.filter(is_active=True).exclude(id_usuario__in=miembros_ids)
    return render(request, 'competitiva/invitar_miembro.html', {
        'equipo': equipo,
        'usuarios_disponibles': usuarios_disponibles
    })


@login_required
def mis_invitaciones(request):
    invitaciones = InvitacionEquipo.objects.filter(
        id_usuario=request.user, estado='pendiente'
    ).select_related('id_equipo', 'id_invitador')
    return render(request, 'competitiva/mis_invitaciones.html', {'invitaciones': invitaciones})


@login_required
def responder_invitacion(request, invitacion_id, accion):
    invitacion = get_object_or_404(
        InvitacionEquipo, id_invitacion=invitacion_id, id_usuario=request.user, estado='pendiente'
    )
    if accion == 'aceptar':
        invitacion.estado = 'aceptada'
        invitacion.fecha_respuesta = timezone.now()
        invitacion.save()
        MiembroEquipo.objects.create(id_equipo=invitacion.id_equipo, id_usuario=request.user, rol='jugador')
        messages.success(request, f'Te has unido a {invitacion.id_equipo.nombre}.')
    elif accion == 'rechazar':
        invitacion.estado = 'rechazada'
        invitacion.fecha_respuesta = timezone.now()
        invitacion.save()
        messages.info(request, 'Invitación rechazada.')
    return redirect('competitiva_mis_invitaciones')


@login_required
def salir_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    if equipo.id_anfitrion == request.user:
        messages.error(request, 'El anfitrión no puede salir del equipo.')
        return redirect('competitiva_detalle_equipo', equipo_id=equipo_id)
    miembro = MiembroEquipo.objects.filter(id_equipo=equipo, id_usuario=request.user).first()
    if miembro:
        miembro.delete()
        messages.success(request, f'Has salido de {equipo.nombre}.')
    return redirect('competitiva_lista_equipos')


def lista_partidos_competitivos(request):
    partidos = PartidoCompetitivo.objects.select_related(
        'id_equipo_local', 'id_equipo_visitante', 'id_localidad'
    ).order_by('-fecha_hora')[:50]
    return render(request, 'competitiva/lista_partidos.html', {'partidos': partidos})


def detalle_partido_competitivo(request, partido_id):
    partido = get_object_or_404(
        PartidoCompetitivo.objects.select_related(
            'id_equipo_local', 'id_equipo_visitante', 'id_cancha', 'id_localidad'
        ),
        id_partido=partido_id
    )
    estadisticas = partido.estadisticas.select_related('id_usuario', 'id_equipo')
    return render(request, 'competitiva/detalle_partido.html', {'partido': partido, 'estadisticas': estadisticas})


@login_required
def crear_partido_competitivo(request, equipo_id):
    equipo_local = get_object_or_404(Equipo, id_equipo=equipo_id)
    miembro = MiembroEquipo.objects.filter(
        id_equipo=equipo_local, id_usuario=request.user, rol__in=['anfitrion', 'capitan']
    ).first()
    if not miembro:
        messages.error(request, 'No tienes permiso para crear partidos para este equipo.')
        return redirect('competitiva_detalle_equipo', equipo_id=equipo_id)
    if request.method == 'POST':
        form = PartidoCompetitivoForm(request.POST)
        if form.is_valid():
            partido = form.save(commit=False)
            partido.id_equipo_local = equipo_local
            partido.id_creador = request.user
            partido.save()
            messages.success(request, 'Partido creado.')
            return redirect('competitiva_detalle_partido', partido_id=partido.id_partido)
    else:
        form = PartidoCompetitivoForm()
        form.fields['id_equipo_visitante'].queryset = Equipo.objects.filter(activo=True).exclude(id_equipo=equipo_id)
    return render(request, 'competitiva/crear_partido.html', {'form': form, 'equipo_local': equipo_local})


@login_required
def mis_equipos(request):
    equipos = Equipo.objects.filter(
        miembros__id_usuario=request.user, miembros__activo=True
    ).distinct().annotate(num_miembros=Count('miembros'))
    return render(request, 'competitiva/mis_equipos.html', {'equipos': equipos})
