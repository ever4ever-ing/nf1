from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Cancha, Recinto
from .forms import RecintoForm, CanchaForm
from eventos.models import Localidad


def lista_canchas(request):
    """Vista para mostrar todas las canchas disponibles"""
    localidad_filtro = request.GET.get('localidad')
    recinto_filtro = request.GET.get('recinto')
    tipo_filtro = request.GET.get('tipo')
    
    canchas = Cancha.objects.select_related(
        'id_recinto__id_localidad'
    ).all()
    
    if localidad_filtro:
        canchas = canchas.filter(id_recinto__id_localidad__id_localidad=localidad_filtro)
    
    if recinto_filtro:
        canchas = canchas.filter(id_recinto__id_recinto=recinto_filtro)
    
    if tipo_filtro:
        canchas = canchas.filter(tipo=tipo_filtro)
    
    # Obtener filtros para el formulario
    localidades = Localidad.objects.all().order_by('nombre')
    recintos = Recinto.objects.select_related('id_localidad').all().order_by('nombre')
    tipos = Cancha.objects.values_list('tipo', flat=True).distinct().exclude(tipo__isnull=True)
    
    context = {
        'canchas': canchas,
        'localidades': localidades,
        'recintos': recintos,
        'tipos': tipos,
        'localidad_filtro': localidad_filtro,
        'recinto_filtro': recinto_filtro,
        'tipo_filtro': tipo_filtro,
    }
    return render(request, 'canchas/lista_canchas.html', context)


@staff_member_required
def crear_recinto(request):
    """Vista para crear un nuevo recinto (solo administradores)"""
    if request.method == 'POST':
        form = RecintoForm(request.POST)
        if form.is_valid():
            recinto = form.save()
            messages.success(request, f'Recinto "{recinto.nombre}" creado exitosamente.')
            return redirect('canchas:lista_recintos')
    else:
        form = RecintoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Recinto'
    }
    return render(request, 'canchas/form_recinto.html', context)


@staff_member_required
def editar_recinto(request, pk):
    """Vista para editar un recinto existente (solo administradores)"""
    recinto = get_object_or_404(Recinto, pk=pk)
    
    if request.method == 'POST':
        form = RecintoForm(request.POST, instance=recinto)
        if form.is_valid():
            recinto = form.save()
            messages.success(request, f'Recinto "{recinto.nombre}" actualizado exitosamente.')
            return redirect('canchas:lista_recintos')
    else:
        form = RecintoForm(instance=recinto)
    
    context = {
        'form': form,
        'titulo': f'Editar Recinto: {recinto.nombre}',
        'recinto': recinto
    }
    return render(request, 'canchas/form_recinto.html', context)


@staff_member_required
def lista_recintos(request):
    """Vista para listar todos los recintos (solo administradores)"""
    recintos = Recinto.objects.select_related('id_localidad').all().order_by('nombre')
    
    context = {
        'recintos': recintos,
    }
    return render(request, 'canchas/lista_recintos.html', context)


@staff_member_required
def crear_cancha(request):
    """Vista para crear una nueva cancha (solo administradores)"""
    if request.method == 'POST':
        form = CanchaForm(request.POST)
        if form.is_valid():
            cancha = form.save()
            messages.success(request, f'Cancha "{cancha.nombre}" creada exitosamente.')
            return redirect('canchas:lista_canchas')
    else:
        form = CanchaForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nueva Cancha'
    }
    return render(request, 'canchas/form_cancha.html', context)


@staff_member_required
def editar_cancha(request, pk):
    """Vista para editar una cancha existente (solo administradores)"""
    cancha = get_object_or_404(Cancha, pk=pk)
    
    if request.method == 'POST':
        form = CanchaForm(request.POST, instance=cancha)
        if form.is_valid():
            cancha = form.save()
            messages.success(request, f'Cancha "{cancha.nombre}" actualizada exitosamente.')
            return redirect('canchas:lista_canchas')
    else:
        form = CanchaForm(instance=cancha)
    
    context = {
        'form': form,
        'titulo': f'Editar Cancha: {cancha.nombre}',
        'cancha': cancha
    }
    return render(request, 'canchas/form_cancha.html', context)
