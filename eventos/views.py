from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Partido, Localidad, ParticipantePartido, Reserva, MensajePartido, Notificacion, Usuario, Recinto, Cancha, Equipo, MiembroEquipo, PartidoCompetitivo, InvitacionEquipo
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
            
            # Procesar reserva de cancha si está marcada
            reserva_creada = None
            if form.cleaned_data.get('reservar_cancha'):
                try:
                    cancha = form.cleaned_data['id_cancha_reserva']
                    fecha_reserva = partido.fecha_inicio
                    hora_inicio = form.cleaned_data['hora_inicio_reserva']
                    hora_fin = form.cleaned_data['hora_fin_reserva']
                    
                    # Crear reserva
                    reserva_creada = Reserva(
                        id_cancha=cancha,
                        id_recinto=cancha.id_recinto,
                        id_usuario=request.user,
                        fecha_reserva=fecha_reserva,
                        hora_inicio=hora_inicio,
                        hora_fin=hora_fin,
                        estado='confirmada'
                    )
                    reserva_creada.full_clean()
                    reserva_creada.save()
                    partido.id_reserva = reserva_creada
                    
                except Exception as e:
                    messages.error(request, f'Error al crear reserva: {str(e)}')
                    return render(request, 'crear_partido.html', {'form': form})
            
            partido.save()
            
            # Automáticamente inscribir al organizador en el partido
            ParticipantePartido.objects.create(
                id_partido=partido,
                id_usuario=request.user
            )
            
            if reserva_creada:
                messages.success(request, f'¡Partido creado exitosamente con reserva de cancha confirmada!')
            else:
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

# ------------------------
# Vistas integradas de canchas (simplificadas)
# ------------------------
from django.contrib.admin.views.decorators import staff_member_required
from .forms import RecintoForm, CanchaForm

@staff_member_required
def lista_canchas(request):
    localidades = Localidad.objects.all().order_by('nombre')
    recinto_filtro = request.GET.get('recinto')
    localidad_filtro = request.GET.get('localidad')
    tipo_filtro = request.GET.get('tipo')
    canchas = Cancha.objects.select_related('id_recinto__id_localidad').all()
    if localidad_filtro:
        canchas = canchas.filter(id_recinto__id_localidad__id_localidad=localidad_filtro)
    if recinto_filtro:
        canchas = canchas.filter(id_recinto__id_recinto=recinto_filtro)
    if tipo_filtro:
        canchas = canchas.filter(tipo=tipo_filtro)
    recintos = Recinto.objects.select_related('id_localidad').all().order_by('nombre')
    tipos = Cancha.objects.values_list('tipo', flat=True).distinct().exclude(tipo__isnull=True)
    return render(request, 'canchas/lista_canchas.html', {
        'canchas': canchas,
        'localidades': localidades,
        'recintos': recintos,
        'tipos': tipos,
        'localidad_filtro': localidad_filtro,
        'recinto_filtro': recinto_filtro,
        'tipo_filtro': tipo_filtro,
    })

@staff_member_required
def lista_recintos(request):
    recintos = Recinto.objects.select_related('id_localidad').all().order_by('nombre')
    return render(request, 'canchas/lista_recintos.html', {'recintos': recintos})

@staff_member_required
def crear_recinto(request):
    if request.method == 'POST':
        form = RecintoForm(request.POST)
        if form.is_valid():
            recinto = form.save()
            messages.success(request, f'Recinto "{recinto.nombre}" creado.')
            return redirect('lista_recintos')
    else:
        form = RecintoForm()
    return render(request, 'canchas/form_recinto.html', {'form': form, 'titulo': 'Crear Nuevo Recinto'})

@staff_member_required
def editar_recinto(request, pk):
    recinto = get_object_or_404(Recinto, pk=pk)
    if request.method == 'POST':
        form = RecintoForm(request.POST, instance=recinto)
        if form.is_valid():
            recinto = form.save()
            messages.success(request, f'Recinto "{recinto.nombre}" actualizado.')
            return redirect('lista_recintos')
    else:
        form = RecintoForm(instance=recinto)
    return render(request, 'canchas/form_recinto.html', {'form': form, 'titulo': f'Editar Recinto: {recinto.nombre}', 'recinto': recinto})

@staff_member_required
def crear_cancha(request):
    if request.method == 'POST':
        form = CanchaForm(request.POST)
        if form.is_valid():
            cancha = form.save()
            messages.success(request, f'Cancha "{cancha.nombre}" creada.')
            return redirect('lista_canchas')
    else:
        form = CanchaForm()
    return render(request, 'canchas/form_cancha.html', {'form': form, 'titulo': 'Crear Nueva Cancha'})

@staff_member_required
def editar_cancha(request, pk):
    cancha = get_object_or_404(Cancha, pk=pk)
    if request.method == 'POST':
        form = CanchaForm(request.POST, instance=cancha)
        if form.is_valid():
            cancha = form.save()
            messages.success(request, f'Cancha "{cancha.nombre}" actualizada.')
            return redirect('lista_canchas')
    else:
        form = CanchaForm(instance=cancha)
    return render(request, 'canchas/form_cancha.html', {'form': form, 'titulo': f'Editar Cancha: {cancha.nombre}', 'cancha': cancha})

# ------------------------
# Vistas de Calendario y Reservas
# ------------------------
from .models import HorarioCancha
from .forms import ReservaForm, HorarioCanchaForm
from datetime import datetime, timedelta

def disponibilidad_cancha(request, cancha_id):
    """Mostrar calendario de disponibilidad de una cancha"""
    cancha = get_object_or_404(Cancha, id_cancha=cancha_id)
    
    # Obtener fecha desde query param o usar hoy
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha = timezone.now().date()
    else:
        fecha = timezone.now().date()
    
    # Calcular rango de fechas para el calendario (próximos 7 días)
    fechas_disponibles = []
    for i in range(14):
        fecha_iter = fecha + timedelta(days=i)
        slots = cancha.get_horarios_disponibles(fecha_iter)
        fechas_disponibles.append({
            'fecha': fecha_iter,
            'slots_count': len(slots),
            'tiene_disponibilidad': len(slots) > 0
        })
    
    # Horarios para la fecha seleccionada
    horarios_disponibles = cancha.get_horarios_disponibles(fecha)
    
    context = {
        'cancha': cancha,
        'fecha_seleccionada': fecha,
        'fechas_disponibles': fechas_disponibles,
        'horarios_disponibles': horarios_disponibles,
    }
    return render(request, 'canchas/disponibilidad_cancha.html', context)

@staff_member_required
def gestionar_horarios_cancha(request, cancha_id):
    """Gestionar horarios de disponibilidad de una cancha (admin)"""
    cancha = get_object_or_404(Cancha, id_cancha=cancha_id)
    horarios = HorarioCancha.objects.filter(id_cancha=cancha).order_by('dia_semana', 'hora_inicio')
    
    if request.method == 'POST':
        form = HorarioCanchaForm(request.POST)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.id_cancha = cancha
            try:
                horario.full_clean()
                horario.save()
                messages.success(request, 'Horario agregado exitosamente.')
                return redirect('gestionar_horarios_cancha', cancha_id=cancha_id)
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = HorarioCanchaForm()
    
    context = {
        'cancha': cancha,
        'horarios': horarios,
        'form': form,
    }
    return render(request, 'canchas/gestionar_horarios.html', context)

@login_required
def crear_reserva(request):
    """Crear una nueva reserva"""
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.id_usuario = request.user
            reserva.id_recinto = reserva.id_cancha.id_recinto
            try:
                reserva.full_clean()
                reserva.save()
                messages.success(request, f'Reserva confirmada para {reserva.fecha_reserva.date()} de {reserva.hora_inicio} a {reserva.hora_fin}.')
                return redirect('mis_reservas')
            except Exception as e:
                messages.error(request, f'Error al crear reserva: {str(e)}')
    else:
        # Prellenar datos si vienen desde disponibilidad_cancha
        initial_data = {}
        if 'cancha' in request.GET:
            initial_data['id_cancha'] = request.GET.get('cancha')
        if 'fecha' in request.GET:
            initial_data['fecha_reserva'] = request.GET.get('fecha')
        if 'hora_inicio' in request.GET:
            initial_data['hora_inicio'] = request.GET.get('hora_inicio')
        if 'hora_fin' in request.GET:
            initial_data['hora_fin'] = request.GET.get('hora_fin')
        form = ReservaForm(initial=initial_data)
    
    return render(request, 'canchas/crear_reserva.html', {'form': form})

@login_required
def mis_reservas(request):
    """Listar reservas del usuario"""
    reservas = Reserva.objects.filter(
        id_usuario=request.user
    ).select_related('id_cancha', 'id_recinto').order_by('-fecha_reserva', '-hora_inicio')
    
    # Separar en futuras y pasadas
    ahora = timezone.now()
    reservas_futuras = reservas.filter(fecha_reserva__gte=ahora.date()).exclude(estado='cancelada')
    reservas_pasadas = reservas.filter(
        DJQ(fecha_reserva__lt=ahora.date()) | DJQ(estado='cancelada')
    )[:20]
    
    context = {
        'reservas_futuras': reservas_futuras,
        'reservas_pasadas': reservas_pasadas,
    }
    return render(request, 'canchas/mis_reservas.html', context)

@login_required
def cancelar_reserva(request, reserva_id):
    """Cancelar una reserva"""
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id, id_usuario=request.user)
    
    if reserva.estado == 'cancelada':
        messages.warning(request, 'Esta reserva ya está cancelada.')
        return redirect('mis_reservas')
    
    if request.method == 'POST':
        reserva.estado = 'cancelada'
        reserva.save()
        messages.success(request, 'Reserva cancelada exitosamente.')
        return redirect('mis_reservas')
    
    return render(request, 'canchas/cancelar_reserva.html', {'reserva': reserva})

def api_horarios_disponibles(request, cancha_id):
    """API endpoint para obtener horarios disponibles (AJAX)"""
    cancha = get_object_or_404(Cancha, id_cancha=cancha_id)
    fecha_str = request.GET.get('fecha')
    duracion = int(request.GET.get('duracion', 90))
    
    if not fecha_str:
        return JsonResponse({'error': 'Fecha requerida'}, status=400)
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
    
    horarios = cancha.get_horarios_disponibles(fecha, duracion)
    
    # Formatear respuesta
    slots = [{
        'hora_inicio': slot['hora_inicio'].strftime('%H:%M'),
        'hora_fin': slot['hora_fin'].strftime('%H:%M'),
        'disponible': slot['disponible']
    } for slot in horarios]
    
    return JsonResponse({
        'cancha': cancha.nombre,
        'fecha': fecha_str,
        'slots': slots
    })

# ------------------------
# Vistas integradas competitiva (simplificadas)
# ------------------------
from .forms import EquipoForm, PartidoCompetitivoForm
from django.db.models import Count, Q as DJQ
from django.utils import timezone

def lista_equipos(request):
    equipos = Equipo.objects.filter(activo=True).annotate(num_miembros=Count('miembros')).order_by('-fecha_creacion')
    return render(request, 'competitiva/lista_equipos.html', {'equipos': equipos})

def detalle_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo.objects.prefetch_related('miembros__id_usuario'), id_equipo=equipo_id)
    miembros = equipo.miembros.filter(activo=True).select_related('id_usuario')
    partidos = PartidoCompetitivo.objects.filter(DJQ(id_equipo_local=equipo) | DJQ(id_equipo_visitante=equipo)).select_related('id_equipo_local', 'id_equipo_visitante').order_by('-fecha_hora')[:10]
    es_miembro = False
    es_anfitrion = False
    invitacion_pendiente = None
    if request.user.is_authenticated:
        es_miembro = miembros.filter(id_usuario=request.user).exists()
        es_anfitrion = equipo.id_anfitrion == request.user
        invitacion_pendiente = InvitacionEquipo.objects.filter(id_equipo=equipo, id_usuario=request.user, estado='pendiente').first()
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
    miembro = MiembroEquipo.objects.filter(id_equipo=equipo, id_usuario=request.user, rol__in=['anfitrion', 'capitan']).first()
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
        InvitacionEquipo.objects.get_or_create(id_equipo=equipo, id_usuario=usuario, defaults={'id_invitador': request.user, 'mensaje': mensaje_texto})
        messages.success(request, f'Invitación enviada a {usuario.nombre}.')
        return redirect('competitiva_detalle_equipo', equipo_id=equipo_id)
    miembros_ids = equipo.miembros.values_list('id_usuario', flat=True)
    usuarios_disponibles = Usuario.objects.filter(is_active=True).exclude(id_usuario__in=miembros_ids)
    return render(request, 'competitiva/invitar_miembro.html', {'equipo': equipo, 'usuarios_disponibles': usuarios_disponibles})

@login_required
def mis_invitaciones(request):
    invitaciones = InvitacionEquipo.objects.filter(id_usuario=request.user, estado='pendiente').select_related('id_equipo', 'id_invitador')
    return render(request, 'competitiva/mis_invitaciones.html', {'invitaciones': invitaciones})

@login_required
def responder_invitacion(request, invitacion_id, accion):
    invitacion = get_object_or_404(InvitacionEquipo, id_invitacion=invitacion_id, id_usuario=request.user, estado='pendiente')
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
    partidos = PartidoCompetitivo.objects.select_related('id_equipo_local', 'id_equipo_visitante', 'id_localidad').order_by('-fecha_hora')[:50]
    return render(request, 'competitiva/lista_partidos.html', {'partidos': partidos})

def detalle_partido_competitivo(request, partido_id):
    partido = get_object_or_404(PartidoCompetitivo.objects.select_related('id_equipo_local', 'id_equipo_visitante', 'id_cancha', 'id_localidad'), id_partido=partido_id)
    estadisticas = partido.estadisticas.select_related('id_usuario', 'id_equipo')
    return render(request, 'competitiva/detalle_partido.html', {'partido': partido, 'estadisticas': estadisticas})

@login_required
def crear_partido_competitivo(request, equipo_id):
    equipo_local = get_object_or_404(Equipo, id_equipo=equipo_id)
    miembro = MiembroEquipo.objects.filter(id_equipo=equipo_local, id_usuario=request.user, rol__in=['anfitrion', 'capitan']).first()
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
    equipos = Equipo.objects.filter(miembros__id_usuario=request.user, miembros__activo=True).distinct().annotate(num_miembros=Count('miembros'))
    return render(request, 'competitiva/mis_equipos.html', {'equipos': equipos})

