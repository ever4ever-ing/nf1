from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def mi_perfil(request):
    return render(request, 'perfil.html', {'usuario': request.user})


@login_required
def editar_perfil(request):
    if request.method == 'POST':
        request.user.nombre = request.POST.get('nombre', request.user.nombre)
        request.user.apellido = request.POST.get('apellido', request.user.apellido)
        request.user.telefono = request.POST.get('telefono', request.user.telefono)
        request.user.biografia = request.POST.get('biografia', request.user.biografia)
        request.user.hobbies = request.POST.get('hobbies', request.user.hobbies)

        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        if fecha_nacimiento:
            request.user.fecha_nacimiento = fecha_nacimiento

        if 'foto_perfil' in request.FILES:
            request.user.foto_perfil = request.FILES['foto_perfil']

        request.user.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('mi_perfil')

    return render(request, 'editar_perfil.html', {'usuario': request.user})
