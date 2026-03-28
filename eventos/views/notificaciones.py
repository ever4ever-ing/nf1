from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..models import Notificacion


@login_required
def mis_notificaciones(request):
    no_leidas = Notificacion.objects.filter(
        id_usuario=request.user,
        leida=False
    ).count()
    notificaciones = Notificacion.objects.filter(
        id_usuario=request.user
    ).select_related(
        'id_partido', 'id_usuario_relacionado', 'id_mensaje__id_usuario'
    ).order_by('-fecha_creacion')[:50]
    return render(request, 'notificaciones.html', {
        'notificaciones': notificaciones,
        'no_leidas': no_leidas,
    })


@login_required
def marcar_notificacion_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id_notificacion=notificacion_id, id_usuario=request.user)
    notificacion.leida = True
    notificacion.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('mis_notificaciones')


@login_required
def marcar_todas_leidas(request):
    Notificacion.objects.filter(id_usuario=request.user, leida=False).update(leida=True)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Todas las notificaciones han sido marcadas como leídas.')
    return redirect('mis_notificaciones')


@login_required
def obtener_notificaciones_nuevas(request):
    count = Notificacion.objects.filter(id_usuario=request.user, leida=False).count()
    return JsonResponse({'count': count})
