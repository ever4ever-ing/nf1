from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Partido, Localidad, ParticipantePartido, Reserva, MensajePartido, Notificacion, Usuario
from django.db.models import Count, Q
from .forms import LoginForm, RegistroForm, MensajePartidoForm, PartidoForm
from django.http import JsonResponse

def index(request):
    """Vista de índice que redirige a la página principal"""
    return render(request, 'index.html')

def home(request):
    """Vista principal que muestra los próximos partidos"""
    partidos = Partido.objects.filter(
        fecha_inicio__gte=timezone.now()
    ).select_related('id_organizador', 'id_localidad').annotate(
        num_participantes=Count('participantes')
    ).order_by('fecha_inicio')[:10]
    
    context = {
        'partidos': partidos,
    }
    return render(request, 'home.html', context)


def lista_partidos(request):
    """Vista que lista todos los partidos disponibles"""
    localidad_filtro = request.GET.get('localidad')
    
    partidos = Partido.objects.select_related(
        'id_organizador', 'id_localidad'
    ).annotate(
        num_participantes=Count('participantes')
    ).order_by('-fecha_inicio')
    
    if localidad_filtro:
        partidos = partidos.filter(id_localidad__id_localidad=localidad_filtro)
    
    # Si el usuario está autenticado, marcar en qué partidos está inscrito
    if request.user.is_authenticated:
        partidos_ids_inscritos = ParticipantePartido.objects.filter(
            id_usuario=request.user
        ).values_list('id_partido_id', flat=True)
        
        for partido in partidos:
            partido.usuario_inscrito = partido.id_partido in partidos_ids_inscritos
    else:
        for partido in partidos:
            partido.usuario_inscrito = False
    
    # Agregar estado de disponibilidad para cada partido
    for partido in partidos:
        partido.casi_lleno = partido.num_participantes >= (partido.max_jugadores * 0.75)
        partido.completo = partido.num_participantes >= partido.max_jugadores
    
    localidades = Localidad.objects.all().order_by('nombre')
    
    context = {
        'partidos': partidos,
        'localidades': localidades,
        'localidad_filtro': localidad_filtro,
    }
    return render(request, 'lista_partidos.html', context)


def detalle_partido(request, partido_id):
    """Vista de detalle de un partido específico con mensajes"""
    partido = get_object_or_404(
        Partido.objects.select_related('id_organizador', 'id_localidad', 'id_reserva')
        .prefetch_related('participantes__id_usuario', 'mensajes__id_usuario'),
        pk=partido_id
    )
    
    participantes = partido.participantes.all()
    esta_inscrito = False
    puede_enviar_mensaje = False
    
    if request.user.is_authenticated:
        esta_inscrito = participantes.filter(id_usuario=request.user).exists()
        # Puede enviar mensajes si es participante o el organizador
        puede_enviar_mensaje = esta_inscrito or partido.id_organizador == request.user
    
    # Obtener mensajes del partido
    mensajes = partido.mensajes.all()
    
    # Manejar envío de mensajes
    if request.method == 'POST' and puede_enviar_mensaje:
        form = MensajePartidoForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.id_partido = partido
            mensaje.id_usuario = request.user
            mensaje.save()
            
            # Crear notificación para el organizador si no es él quien escribe
            if partido.id_organizador != request.user:
                Notificacion.objects.create(
                    id_usuario=partido.id_organizador,
                    id_partido=partido,
                    tipo='nuevo_mensaje',
                    mensaje=f"{request.user.nombre} escribió un mensaje en '{partido.lugar}'",
                    id_usuario_relacionado=request.user,
                    id_mensaje=mensaje
                )
            
            messages.success(request, 'Mensaje enviado correctamente.')
            return redirect('detalle_partido', partido_id=partido_id)
    else:
        form = MensajePartidoForm()
    
    context = {
        'partido': partido,
        'participantes': participantes,
        'esta_inscrito': esta_inscrito,
        'espacios_disponibles': partido.espacios_disponibles(),
        'mensajes': mensajes,
        'form': form,
        'puede_enviar_mensaje': puede_enviar_mensaje,
    }
    return render(request, 'detalle_partido.html', context)


@login_required
def unirse_partido(request, partido_id):
    """Vista para que un usuario se una a un partido"""
    partido = get_object_or_404(Partido, pk=partido_id)
    
    # Verificar si hay espacio disponible
    if partido.espacios_disponibles() <= 0:
        messages.error(request, 'Este partido ya está completo.')
        return redirect('detalle_partido', partido_id=partido_id)
    
    # Verificar si el usuario ya está inscrito
    ya_inscrito = ParticipantePartido.objects.filter(
        id_partido=partido,
        id_usuario=request.user
    ).exists()
    
    if ya_inscrito:
        messages.warning(request, 'Ya estás inscrito en este partido.')
    else:
        ParticipantePartido.objects.create(
            id_partido=partido,
            id_usuario=request.user
        )
        
        # Agregar 10 puntos al usuario que se une
        request.user.agregar_puntos_participacion()
        
        # Agregar 5 puntos al organizador
        partido.id_organizador.agregar_puntos_organizador(1)
        
        # Crear notificación para el organizador
        Notificacion.objects.create(
            id_usuario=partido.id_organizador,
            id_partido=partido,
            tipo='nuevo_participante',
            mensaje=f"{request.user.nombre} se ha unido a '{partido.lugar}' (+5 puntos)",
            id_usuario_relacionado=request.user
        )
        
        messages.success(request, '¡Te has unido al partido exitosamente! (+10 puntos Friendly)')
    
    return redirect('detalle_partido', partido_id=partido_id)


@login_required
def salir_partido(request, partido_id):
    """Vista para que un usuario salga de un partido"""
    partido = get_object_or_404(Partido, pk=partido_id)
    
    participante = ParticipantePartido.objects.filter(
        id_partido=partido,
        id_usuario=request.user
    ).first()
    
    if participante:
        participante.delete()
        
        # Crear notificación para el organizador
        Notificacion.objects.create(
            id_usuario=partido.id_organizador,
            id_partido=partido,
            tipo='salida_participante',
            mensaje=f"{request.user.nombre} ha salido de '{partido.lugar}'",
            id_usuario_relacionado=request.user
        )
        
        messages.success(request, 'Has salido del partido.')
    else:
        messages.warning(request, 'No estabas inscrito en este partido.')
    
    return redirect('detalle_partido', partido_id=partido_id)


@login_required
def mis_partidos(request):
    """Vista que muestra los partidos del usuario"""
    # Partidos organizados por el usuario
    partidos_organizados = Partido.objects.filter(
        id_organizador=request.user
    ).annotate(
        num_participantes=Count('participantes')
    ).order_by('-fecha_inicio')
    
    # Partidos en los que participa
    partidos_participando = Partido.objects.filter(
        participantes__id_usuario=request.user
    ).annotate(
        num_participantes=Count('participantes')
    ).order_by('-fecha_inicio')
    
    context = {
        'partidos_organizados': partidos_organizados,
        'partidos_participando': partidos_participando,
    }
    return render(request, 'mis_partidos.html', context)


def login_view(request):
    """Vista para el login de usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.nombre}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Email o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def registro_view(request):
    """Vista para el registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido {user.nombre}!')
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    
    return render(request, 'registro.html', {'form': form})


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, '¡Sesión cerrada exitosamente!')
    return redirect('home')


@login_required
def mis_notificaciones(request):
    """Vista para mostrar las notificaciones del usuario"""
    # Contar notificaciones no leídas primero
    no_leidas = Notificacion.objects.filter(
        id_usuario=request.user,
        leida=False
    ).count()
    
    # Luego obtener las notificaciones limitadas
    notificaciones = Notificacion.objects.filter(
        id_usuario=request.user
    ).select_related(
        'id_partido', 'id_usuario_relacionado', 'id_mensaje__id_usuario'
    ).order_by('-fecha_creacion')[:50]
    
    context = {
        'notificaciones': notificaciones,
        'no_leidas': no_leidas,
    }
    return render(request, 'notificaciones.html', context)


@login_required
def marcar_notificacion_leida(request, notificacion_id):
    """Vista para marcar una notificación como leída"""
    notificacion = get_object_or_404(Notificacion, id_notificacion=notificacion_id, id_usuario=request.user)
    notificacion.leida = True
    notificacion.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('mis_notificaciones')


@login_required
def marcar_todas_leidas(request):
    """Vista para marcar todas las notificaciones como leídas"""
    Notificacion.objects.filter(id_usuario=request.user, leida=False).update(leida=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Todas las notificaciones han sido marcadas como leídas.')
    return redirect('mis_notificaciones')


@login_required
def obtener_notificaciones_nuevas(request):
    """API para obtener el conteo de notificaciones nuevas (AJAX)"""
    count = Notificacion.objects.filter(id_usuario=request.user, leida=False).count()
    return JsonResponse({'count': count})


@login_required
def mi_perfil(request):
    """Vista para ver y editar el perfil del usuario"""
    return render(request, 'perfil.html', {'usuario': request.user})


@login_required
def editar_perfil(request):
    """Vista para editar el perfil del usuario"""
    if request.method == 'POST':
        # Actualizar datos básicos
        request.user.nombre = request.POST.get('nombre', request.user.nombre)
        request.user.apellido = request.POST.get('apellido', request.user.apellido)
        request.user.telefono = request.POST.get('telefono', request.user.telefono)
        request.user.biografia = request.POST.get('biografia', request.user.biografia)
        request.user.hobbies = request.POST.get('hobbies', request.user.hobbies)
        
        # Actualizar fecha de nacimiento
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        if fecha_nacimiento:
            request.user.fecha_nacimiento = fecha_nacimiento
        
        # Actualizar foto de perfil
        if 'foto_perfil' in request.FILES:
            request.user.foto_perfil = request.FILES['foto_perfil']
        
        request.user.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('mi_perfil')
    
    return render(request, 'editar_perfil.html', {'usuario': request.user})


def ver_perfil_usuario(request, usuario_id):
    """Vista pública para ver el perfil de otro usuario"""
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    # Obtener estadísticas del usuario
    partidos_organizados = Partido.objects.filter(id_organizador=usuario).count()
    partidos_participados = ParticipantePartido.objects.filter(id_usuario=usuario).count()
    
    context = {
        'usuario': usuario,
        'partidos_organizados': partidos_organizados,
        'partidos_participados': partidos_participados,
    }
    return render(request, 'ver_perfil.html', context)


@login_required
def ranking_usuarios(request):
    """Vista para mostrar el ranking de usuarios por puntos"""
    usuarios = Usuario.objects.filter(is_active=True).order_by('-puntos_friendly')[:50]
    
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'ranking.html', context)


@login_required
def crear_partido(request):
    """Vista para que un usuario pueda crear/organizar un nuevo partido"""
    if request.method == 'POST':
        form = PartidoForm(request.POST)
        if form.is_valid():
            partido = form.save(commit=False)
            partido.id_organizador = request.user
            partido.save()
            
            # Automáticamente inscribir al organizador en el partido
            ParticipantePartido.objects.create(
                id_partido=partido,
                id_usuario=request.user
            )
            
            messages.success(request, f'¡Partido creado exitosamente! Ahora otros jugadores podrán unirse.')
            return redirect('detalle_partido', partido_id=partido.id_partido)
    else:
        form = PartidoForm()
    
    context = {
        'form': form,
    }
    return render(request, 'crear_partido.html', context)


@login_required
def editar_partido(request, partido_id):
    """Vista para que el organizador pueda editar su partido"""
    partido = get_object_or_404(Partido, id_partido=partido_id)
    
    # Verificar que el usuario sea el organizador
    if partido.id_organizador != request.user:
        messages.error(request, 'No tienes permiso para editar este partido.')
        return redirect('detalle_partido', partido_id=partido.id_partido)
    
    if request.method == 'POST':
        form = PartidoForm(request.POST, instance=partido)
        if form.is_valid():
            form.save()
            
            # Notificar a todos los participantes del cambio
            participantes = ParticipantePartido.objects.filter(id_partido=partido).exclude(id_usuario=request.user)
            for participante in participantes:
                Notificacion.objects.create(
                    id_usuario=participante.id_usuario,
                    tipo='info',
                    mensaje=f'El partido "{partido.lugar}" ha sido actualizado por el organizador.',
                    id_partido=partido
                )
            
            messages.success(request, 'Partido actualizado exitosamente.')
            return redirect('detalle_partido', partido_id=partido.id_partido)
    else:
        # Formatear la fecha para el campo datetime-local
        initial_data = {
            'lugar': partido.lugar,
            'fecha_inicio': partido.fecha_inicio.strftime('%Y-%m-%dT%H:%M') if partido.fecha_inicio else '',
            'id_localidad': partido.id_localidad,
            'max_jugadores': partido.max_jugadores,
            'descripcion': partido.descripcion,
        }
        form = PartidoForm(instance=partido, initial=initial_data)
    
    context = {
        'form': form,
        'partido': partido,
    }
    return render(request, 'editar_partido.html', context)


@login_required
def cancelar_partido(request, partido_id):
    """Vista para que el organizador pueda cancelar su partido"""
    partido = get_object_or_404(Partido, id_partido=partido_id)
    
    # Verificar que el usuario sea el organizador
    if partido.id_organizador != request.user:
        messages.error(request, 'No tienes permiso para cancelar este partido.')
        return redirect('detalle_partido', partido_id=partido.id_partido)
    
    if request.method == 'POST':
        # Notificar a todos los participantes
        participantes = ParticipantePartido.objects.filter(id_partido=partido).exclude(id_usuario=request.user)
        for participante in participantes:
            Notificacion.objects.create(
                id_usuario=participante.id_usuario,
                tipo='cancelacion',
                mensaje=f'El partido "{partido.lugar}" del {partido.fecha_inicio.strftime("%d/%m/%Y %H:%M")} ha sido cancelado.',
                id_partido=partido
            )
        
        partido.delete()
        messages.success(request, 'Partido cancelado exitosamente.')
        return redirect('mis_partidos')
    
    context = {
        'partido': partido,
    }
    return render(request, 'cancelar_partido.html', context)

