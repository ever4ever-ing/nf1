from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import MensajePartidoForm, PartidoCrearForm, PartidoEditForm
from ..models import Cancha, Localidad, MensajePartido, Notificacion, ParticipantePartido, Partido, Reserva


def _initial_partido_form_desde_querystring(request):
    """Prefill crear partido desde ?cancha=&fecha=&hora_inicio=&hora_fin= (p. ej. desde disponibilidad)."""
    get = request.GET
    cancha_id = get.get('cancha')
    if not cancha_id:
        return {}
    try:
        cancha = Cancha.objects.select_related('id_recinto__id_localidad').get(pk=cancha_id)
    except (Cancha.DoesNotExist, ValueError):
        return {}

    initial = {
        'id_cancha_reserva': cancha.pk,
    }

    def _parse_time(s):
        if not s:
            return None
        s = s.strip()
        for fmt in ('%H:%M:%S', '%H:%M'):
            try:
                return datetime.strptime(s, fmt).time()
            except ValueError:
                continue
        return None

    fecha_s = get.get('fecha')
    hora_ini_s = get.get('hora_inicio') or get.get('hora')
    hora_fin_s = get.get('hora_fin')
    ti = _parse_time(hora_ini_s)
    tf = _parse_time(hora_fin_s)
    if ti:
        initial['hora_inicio_reserva'] = ti.strftime('%H:%M')
    if tf:
        initial['hora_fin_reserva'] = tf.strftime('%H:%M')

    d = None
    if fecha_s:
        try:
            d = datetime.strptime(fecha_s, '%Y-%m-%d').date()
        except ValueError:
            d = None
    if d:
        initial['fecha_reserva'] = d

    return initial


def lista_partidos(request):
    localidad_filtro = request.GET.get('localidad')
    partidos = Partido.objects.select_related(
        'id_organizador', 'id_localidad'
    ).annotate(
        num_participantes=Count('participantes')
    ).order_by('-fecha_inicio')

    if localidad_filtro:
        partidos = partidos.filter(id_localidad__id_localidad=localidad_filtro)

    if request.user.is_authenticated:
        partidos_ids_inscritos = ParticipantePartido.objects.filter(
            id_usuario=request.user
        ).values_list('id_partido_id', flat=True)
        for partido in partidos:
            partido.usuario_inscrito = partido.id_partido in partidos_ids_inscritos
    else:
        for partido in partidos:
            partido.usuario_inscrito = False

    for partido in partidos:
        partido.casi_lleno = partido.num_participantes >= (partido.max_jugadores * 0.75)
        partido.completo = partido.num_participantes >= partido.max_jugadores

    localidades = Localidad.objects.all().order_by('nombre')
    return render(request, 'lista_partidos.html', {
        'partidos': partidos,
        'localidades': localidades,
        'localidad_filtro': localidad_filtro,
    })


def detalle_partido(request, partido_id):
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
        puede_enviar_mensaje = esta_inscrito or partido.id_organizador == request.user

    mensajes = partido.mensajes.all()

    if request.method == 'POST' and puede_enviar_mensaje:
        form = MensajePartidoForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.id_partido = partido
            mensaje.id_usuario = request.user
            mensaje.save()
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

    return render(request, 'detalle_partido.html', {
        'partido': partido,
        'participantes': participantes,
        'esta_inscrito': esta_inscrito,
        'espacios_disponibles': partido.espacios_disponibles(),
        'mensajes': mensajes,
        'form': form,
        'puede_enviar_mensaje': puede_enviar_mensaje,
    })


@login_required
def unirse_partido(request, partido_id):
    partido = get_object_or_404(Partido, pk=partido_id)
    if partido.espacios_disponibles() <= 0:
        messages.error(request, 'Este partido ya está completo.')
        return redirect('detalle_partido', partido_id=partido_id)

    ya_inscrito = ParticipantePartido.objects.filter(
        id_partido=partido,
        id_usuario=request.user
    ).exists()

    if ya_inscrito:
        messages.warning(request, 'Ya estás inscrito en este partido.')
    else:
        ParticipantePartido.objects.create(id_partido=partido, id_usuario=request.user)
        request.user.agregar_puntos_participacion()
        partido.id_organizador.agregar_puntos_organizador(1)
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
    partido = get_object_or_404(Partido, pk=partido_id)
    participante = ParticipantePartido.objects.filter(
        id_partido=partido,
        id_usuario=request.user
    ).first()

    if participante:
        participante.delete()
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
    partidos_organizados = Partido.objects.filter(
        id_organizador=request.user
    ).annotate(
        num_participantes=Count('participantes')
    ).order_by('-fecha_inicio')
    partidos_participando = Partido.objects.filter(
        participantes__id_usuario=request.user
    ).annotate(
        num_participantes=Count('participantes')
    ).order_by('-fecha_inicio')
    return render(request, 'mis_partidos.html', {
        'partidos_organizados': partidos_organizados,
        'partidos_participando': partidos_participando,
    })


@login_required
def crear_partido(request):
    if request.method == 'POST':
        form = PartidoCrearForm(request.POST)
        if form.is_valid():
            partido = form.save(commit=False)
            partido.id_organizador = request.user
            try:
                cancha = form.cleaned_data['id_cancha_reserva']
                fecha_reserva = form.cleaned_data['fecha_reserva']
                hora_inicio = form.cleaned_data['hora_inicio_reserva']
                hora_fin = form.cleaned_data['hora_fin_reserva']
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
            ParticipantePartido.objects.create(id_partido=partido, id_usuario=request.user)
            messages.success(request, '¡Partido creado exitosamente con reserva de cancha confirmada!')
            return redirect('detalle_partido', partido_id=partido.id_partido)
    else:
        form = PartidoCrearForm(initial=_initial_partido_form_desde_querystring(request))

    return render(request, 'crear_partido.html', {'form': form})


@login_required
def editar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id_partido=partido_id)
    if partido.id_organizador != request.user:
        messages.error(request, 'No tienes permiso para editar este partido.')
        return redirect('detalle_partido', partido_id=partido.id_partido)

    if request.method == 'POST':
        form = PartidoEditForm(request.POST, instance=partido)
        if form.is_valid():
            form.save()
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
        initial_data = {
            'lugar': partido.lugar,
            'fecha_inicio': partido.fecha_inicio.strftime('%Y-%m-%dT%H:%M') if partido.fecha_inicio else '',
            'id_localidad': partido.id_localidad,
            'max_jugadores': partido.max_jugadores,
            'descripcion': partido.descripcion,
        }
        form = PartidoEditForm(instance=partido, initial=initial_data)

    return render(request, 'editar_partido.html', {'form': form, 'partido': partido})


@login_required
def cancelar_partido(request, partido_id):
    partido = get_object_or_404(Partido, id_partido=partido_id)
    if partido.id_organizador != request.user:
        messages.error(request, 'No tienes permiso para cancelar este partido.')
        return redirect('detalle_partido', partido_id=partido.id_partido)

    if request.method == 'POST':
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

    return render(request, 'cancelar_partido.html', {'partido': partido})
