from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Equipo, MiembroEquipo, PartidoCompetitivo, InvitacionEquipo, EstadisticaJugador
from .forms import EquipoForm, PartidoCompetitivoForm, InvitacionEquipoForm, ActualizarResultadoForm
from eventos.models import Usuario


def lista_equipos(request):
    """Lista todos los equipos activos"""
    equipos = Equipo.objects.filter(activo=True).annotate(
        num_miembros=Count('miembros')
    ).order_by('-fecha_creacion')
    
    context = {
        'equipos': equipos,
    }
    return render(request, 'competitiva/lista_equipos.html', context)


def detalle_equipo(request, equipo_id):
    """Detalle de un equipo"""
    equipo = get_object_or_404(
        Equipo.objects.prefetch_related('miembros__id_usuario'),
        id_equipo=equipo_id
    )
    
    miembros = equipo.miembros.filter(activo=True).select_related('id_usuario')
    partidos = PartidoCompetitivo.objects.filter(
        Q(id_equipo_local=equipo) | Q(id_equipo_visitante=equipo)
    ).select_related('id_equipo_local', 'id_equipo_visitante').order_by('-fecha_hora')[:10]
    
    es_miembro = False
    es_anfitrion = False
    invitacion_pendiente = None
    
    if request.user.is_authenticated:
        es_miembro = miembros.filter(id_usuario=request.user).exists()
        es_anfitrion = equipo.id_anfitrion == request.user
        invitacion_pendiente = InvitacionEquipo.objects.filter(
            id_equipo=equipo,
            id_usuario=request.user,
            estado='pendiente'
        ).first()
    
    context = {
        'equipo': equipo,
        'miembros': miembros,
        'partidos': partidos,
        'es_miembro': es_miembro,
        'es_anfitrion': es_anfitrion,
        'invitacion_pendiente': invitacion_pendiente,
    }
    return render(request, 'competitiva/detalle_equipo.html', context)


@login_required
def crear_equipo(request):
    """Crear un nuevo equipo"""
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save(commit=False)
            equipo.id_anfitrion = request.user
            equipo.save()
            
            # Agregar al creador como miembro con rol anfitrion
            MiembroEquipo.objects.create(
                id_equipo=equipo,
                id_usuario=request.user,
                rol='anfitrion'
            )
            
            messages.success(request, f'Equipo "{equipo.nombre}" creado exitosamente.')
            return redirect('detalle_equipo', equipo_id=equipo.id_equipo)
    else:
        form = EquipoForm()
    
    return render(request, 'competitiva/crear_equipo.html', {'form': form})


@login_required
def editar_equipo(request, equipo_id):
    """Editar un equipo (solo anfitrión)"""
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    
    if equipo.id_anfitrion != request.user:
        messages.error(request, 'No tienes permiso para editar este equipo.')
        return redirect('detalle_equipo', equipo_id=equipo_id)
    
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo actualizado exitosamente.')
            return redirect('detalle_equipo', equipo_id=equipo_id)
    else:
        form = EquipoForm(instance=equipo)
    
    return render(request, 'competitiva/editar_equipo.html', {'form': form, 'equipo': equipo})


@login_required
def invitar_miembro(request, equipo_id):
    """Invitar un usuario al equipo"""
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    
    # Verificar que el usuario es anfitrión o capitán
    miembro = MiembroEquipo.objects.filter(
        id_equipo=equipo,
        id_usuario=request.user,
        rol__in=['anfitrion', 'capitan']
    ).first()
    
    if not miembro:
        messages.error(request, 'No tienes permiso para invitar miembros.')
        return redirect('detalle_equipo', equipo_id=equipo_id)
    
    if request.method == 'POST':
        usuario_id = request.POST.get('id_usuario')
        mensaje = request.POST.get('mensaje', '')
        
        usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
        
        # Verificar que no es miembro ya
        if MiembroEquipo.objects.filter(id_equipo=equipo, id_usuario=usuario).exists():
            messages.warning(request, 'Este usuario ya es miembro del equipo.')
            return redirect('detalle_equipo', equipo_id=equipo_id)
        
        # Crear invitación
        InvitacionEquipo.objects.get_or_create(
            id_equipo=equipo,
            id_usuario=usuario,
            defaults={'id_invitador': request.user, 'mensaje': mensaje}
        )
        
        messages.success(request, f'Invitación enviada a {usuario.nombre}.')
        return redirect('detalle_equipo', equipo_id=equipo_id)
    
    # Obtener usuarios que no son miembros
    miembros_ids = equipo.miembros.values_list('id_usuario', flat=True)
    usuarios_disponibles = Usuario.objects.filter(is_active=True).exclude(id_usuario__in=miembros_ids)
    
    context = {
        'equipo': equipo,
        'usuarios_disponibles': usuarios_disponibles,
    }
    return render(request, 'competitiva/invitar_miembro.html', context)


@login_required
def mis_invitaciones(request):
    """Ver invitaciones pendientes"""
    invitaciones = InvitacionEquipo.objects.filter(
        id_usuario=request.user,
        estado='pendiente'
    ).select_related('id_equipo', 'id_invitador')
    
    context = {
        'invitaciones': invitaciones,
    }
    return render(request, 'competitiva/mis_invitaciones.html', context)


@login_required
def responder_invitacion(request, invitacion_id, accion):
    """Aceptar o rechazar invitación"""
    invitacion = get_object_or_404(
        InvitacionEquipo,
        id_invitacion=invitacion_id,
        id_usuario=request.user,
        estado='pendiente'
    )
    
    if accion == 'aceptar':
        invitacion.estado = 'aceptada'
        invitacion.fecha_respuesta = timezone.now()
        invitacion.save()
        
        # Agregar como miembro
        MiembroEquipo.objects.create(
            id_equipo=invitacion.id_equipo,
            id_usuario=request.user,
            rol='jugador'
        )
        
        messages.success(request, f'Te has unido a {invitacion.id_equipo.nombre}.')
    elif accion == 'rechazar':
        invitacion.estado = 'rechazada'
        invitacion.fecha_respuesta = timezone.now()
        invitacion.save()
        
        messages.info(request, 'Invitación rechazada.')
    
    return redirect('mis_invitaciones')


@login_required
def salir_equipo(request, equipo_id):
    """Salir de un equipo"""
    equipo = get_object_or_404(Equipo, id_equipo=equipo_id)
    
    if equipo.id_anfitrion == request.user:
        messages.error(request, 'El anfitrión no puede salir del equipo. Debes transferir el rol primero.')
        return redirect('detalle_equipo', equipo_id=equipo_id)
    
    miembro = MiembroEquipo.objects.filter(
        id_equipo=equipo,
        id_usuario=request.user
    ).first()
    
    if miembro:
        miembro.delete()
        messages.success(request, f'Has salido de {equipo.nombre}.')
    
    return redirect('lista_equipos')


def lista_partidos_competitivos(request):
    """Lista de partidos competitivos"""
    partidos = PartidoCompetitivo.objects.select_related(
        'id_equipo_local', 'id_equipo_visitante', 'id_localidad'
    ).order_by('-fecha_hora')[:50]
    
    context = {
        'partidos': partidos,
    }
    return render(request, 'competitiva/lista_partidos.html', context)


def detalle_partido_competitivo(request, partido_id):
    """Detalle de un partido competitivo"""
    partido = get_object_or_404(
        PartidoCompetitivo.objects.select_related(
            'id_equipo_local', 'id_equipo_visitante', 'id_cancha', 'id_localidad'
        ),
        id_partido=partido_id
    )
    
    estadisticas = partido.estadisticas.select_related('id_usuario', 'id_equipo')
    
    context = {
        'partido': partido,
        'estadisticas': estadisticas,
    }
    return render(request, 'competitiva/detalle_partido.html', context)


@login_required
def crear_partido_competitivo(request, equipo_id):
    """Crear un partido competitivo"""
    equipo_local = get_object_or_404(Equipo, id_equipo=equipo_id)
    
    # Verificar que es anfitrión o capitán
    miembro = MiembroEquipo.objects.filter(
        id_equipo=equipo_local,
        id_usuario=request.user,
        rol__in=['anfitrion', 'capitan']
    ).first()
    
    if not miembro:
        messages.error(request, 'No tienes permiso para crear partidos para este equipo.')
        return redirect('detalle_equipo', equipo_id=equipo_id)
    
    if request.method == 'POST':
        form = PartidoCompetitivoForm(request.POST)
        if form.is_valid():
            partido = form.save(commit=False)
            partido.id_equipo_local = equipo_local
            partido.id_creador = request.user
            partido.save()
            
            messages.success(request, 'Partido creado exitosamente.')
            return redirect('detalle_partido_competitivo', partido_id=partido.id_partido)
    else:
        form = PartidoCompetitivoForm()
        # Excluir el equipo local de las opciones
        form.fields['id_equipo_visitante'].queryset = Equipo.objects.filter(activo=True).exclude(id_equipo=equipo_id)
    
    context = {
        'form': form,
        'equipo_local': equipo_local,
    }
    return render(request, 'competitiva/crear_partido.html', context)


@login_required
def mis_equipos(request):
    """Ver equipos del usuario"""
    equipos = Equipo.objects.filter(
        miembros__id_usuario=request.user,
        miembros__activo=True
    ).distinct().annotate(
        num_miembros=Count('miembros')
    )
    
    context = {
        'equipos': equipos,
    }
    return render(request, 'competitiva/mis_equipos.html', context)

