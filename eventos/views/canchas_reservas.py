from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q as DJQ
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, TemplateView

from ..admin_recintos import (
    GestionCanchasMixin,
    SoloAdminSitioMixin,
    contexto_edicion_canchas,
    puede_gestionar_cancha,
    recintos_para_dropdown_cancha,
    usuario_es_admin_sitio,
)
from ..forms import CanchaForm, HorarioCanchaForm, RecintoForm, ReservaForm
from ..models import Cancha, HorarioCancha, Localidad, Recinto, Reserva


class ListaCanchasView(TemplateView):
    template_name = 'canchas/lista_canchas.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        request = self.request
        localidades = Localidad.objects.all().order_by('nombre')
        recinto_filtro = request.GET.get('recinto')
        localidad_filtro = request.GET.get('localidad')
        tipo_filtro = request.GET.get('tipo')
        canchas = Cancha.objects.select_related('id_recinto__id_localidad').prefetch_related('horarios').all()
        if localidad_filtro:
            canchas = canchas.filter(id_recinto__id_localidad__id_localidad=localidad_filtro)
        if recinto_filtro:
            canchas = canchas.filter(id_recinto__id_recinto=recinto_filtro)
        if tipo_filtro:
            canchas = canchas.filter(tipo=tipo_filtro)
        recintos = Recinto.objects.select_related('id_localidad').all().order_by('nombre')
        tipos = Cancha.objects.values_list('tipo', flat=True).distinct().exclude(tipo__isnull=True)

        canchas_list = list(canchas)
        hoy = timezone.now().date()
        duracion_slot = 120
        canchas_con_slots = []
        for c in canchas_list:
            slots_hoy = c.get_horarios_disponibles(hoy, duracion_minutos=duracion_slot)
            canchas_con_slots.append({
                'cancha': c,
                'slots_hoy': slots_hoy,
            })

        ctx.update({
            'canchas': canchas_list,
            'canchas_con_slots': canchas_con_slots,
            'fecha_disponibilidad_listado': hoy,
            'duracion_slot_minutos': duracion_slot,
            'localidades': localidades,
            'recintos': recintos,
            'tipos': tipos,
            'localidad_filtro': localidad_filtro,
            'recinto_filtro': recinto_filtro,
            'tipo_filtro': tipo_filtro,
        })
        ctx.update(contexto_edicion_canchas(request.user, canchas_list))
        return ctx


class ListaRecintosView(SoloAdminSitioMixin, TemplateView):
    template_name = 'canchas/lista_recintos.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Recinto.objects.select_related('id_localidad').order_by('nombre')
        ctx['recintos'] = qs
        return ctx


class CrearRecintoView(SoloAdminSitioMixin, FormView):
    form_class = RecintoForm
    template_name = 'canchas/form_recinto.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Crear Nuevo Recinto'
        return ctx

    def form_valid(self, form):
        recinto = form.save()
        messages.success(self.request, f'Recinto "{recinto.nombre}" creado.')
        return redirect('lista_recintos')


class EditarRecintoView(SoloAdminSitioMixin, FormView):
    form_class = RecintoForm
    template_name = 'canchas/form_recinto.html'

    def dispatch(self, request, *args, **kwargs):
        self.recinto = get_object_or_404(Recinto, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.recinto
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar Recinto: {self.recinto.nombre}'
        ctx['recinto'] = self.recinto
        return ctx

    def form_valid(self, form):
        recinto = form.save()
        messages.success(self.request, f'Recinto "{recinto.nombre}" actualizado.')
        return redirect('lista_recintos')


class CrearCanchaView(GestionCanchasMixin, FormView):
    form_class = CanchaForm
    template_name = 'canchas/form_cancha.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = 'Crear Nueva Cancha'
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['id_recinto'].queryset = recintos_para_dropdown_cancha(self.request.user).order_by('nombre')
        return form

    def form_valid(self, form):
        cancha = form.save(commit=False)
        if not puede_gestionar_cancha(self.request.user, cancha):
            messages.error(self.request, 'No puedes crear canchas en ese recinto.')
            return self.form_invalid(form)
        cancha.save()
        messages.success(self.request, f'Cancha "{cancha.nombre}" creada.')
        return redirect('lista_canchas')


class EditarCanchaView(GestionCanchasMixin, FormView):
    form_class = CanchaForm
    template_name = 'canchas/form_cancha.html'

    def dispatch(self, request, *args, **kwargs):
        qs = Cancha.objects.select_related('id_recinto')
        if not usuario_es_admin_sitio(request.user):
            qs = qs.filter(id_recinto__in=request.user.recintos_gestion.all())
        self.cancha = get_object_or_404(qs, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.cancha
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['id_recinto'].queryset = recintos_para_dropdown_cancha(self.request.user).order_by('nombre')
        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar Cancha: {self.cancha.nombre}'
        ctx['cancha'] = self.cancha
        return ctx

    def form_valid(self, form):
        cancha = form.save(commit=False)
        if not puede_gestionar_cancha(self.request.user, cancha):
            messages.error(self.request, 'No puedes asignar esa cancha a ese recinto.')
            return self.form_invalid(form)
        cancha.save()
        messages.success(self.request, f'Cancha "{cancha.nombre}" actualizada.')
        return redirect('lista_canchas')


class DisponibilidadCanchaView(TemplateView):
    template_name = 'disponibilidad_cancha.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        request = self.request
        canchas = Cancha.objects.select_related('id_recinto').all()
        cancha_id = request.GET.get('cancha_id')
        cancha_seleccionada = None
        fechas_disponibles = []
        puede_gestionar_horarios = False

        if cancha_id:
            cancha_seleccionada = get_object_or_404(Cancha, id_cancha=cancha_id)
            puede_gestionar_horarios = puede_gestionar_cancha(request.user, cancha_seleccionada)
            fecha_str = request.GET.get('fecha')
            if fecha_str:
                try:
                    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                except ValueError:
                    fecha = timezone.now().date()
            else:
                fecha = timezone.now().date()

            for i in range(14):
                fecha_iter = fecha + timedelta(days=i)
                horarios = cancha_seleccionada.get_horarios_disponibles(fecha_iter, duracion_minutos=120)
                fechas_disponibles.append({'fecha': fecha_iter, 'horarios': horarios})

        ctx.update({
            'canchas': canchas,
            'cancha_id': cancha_id,
            'cancha_seleccionada': cancha_seleccionada,
            'fechas_disponibles': fechas_disponibles,
            'puede_gestionar_horarios_cancha': puede_gestionar_horarios,
        })
        return ctx


class GestionarHorariosCanchaView(GestionCanchasMixin, TemplateView):
    template_name = 'gestionar_horarios.html'

    def dispatch(self, request, *args, **kwargs):
        qs = Cancha.objects.select_related('id_recinto')
        if not usuario_es_admin_sitio(request.user):
            qs = qs.filter(id_recinto__in=request.user.recintos_gestion.all())
        self.cancha = get_object_or_404(qs, id_cancha=kwargs['cancha_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        horarios = HorarioCancha.objects.filter(id_cancha=self.cancha).order_by('dia_semana', 'hora_inicio')
        ctx.update({
            'cancha': self.cancha,
            'horarios': horarios,
            'form': HorarioCanchaForm(cancha=self.cancha),
        })
        return ctx

    def post(self, request, *args, **kwargs):
        form = HorarioCanchaForm(request.POST, cancha=self.cancha)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.id_cancha = self.cancha
            try:
                horario.save()
                messages.success(request, 'Horario agregado exitosamente.')
                return redirect('gestionar_horarios_cancha', cancha_id=kwargs['cancha_id'])
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        ctx = self.get_context_data(**kwargs)
        ctx['form'] = form
        return self.render_to_response(ctx)


class CrearReservaView(LoginRequiredMixin, FormView):
    form_class = ReservaForm
    template_name = 'canchas/crear_reserva.html'

    def get_initial(self):
        initial = super().get_initial()
        q = self.request.GET
        if 'cancha' in q:
            initial['id_cancha'] = q.get('cancha')
        if 'fecha' in q:
            initial['fecha_reserva'] = q.get('fecha')
        if 'hora_inicio' in q:
            initial['hora_inicio'] = q.get('hora_inicio')
        if 'hora_fin' in q:
            initial['hora_fin'] = q.get('hora_fin')
        return initial

    def form_valid(self, form):
        reserva = form.save(commit=False)
        reserva.id_usuario = self.request.user
        reserva.id_recinto = reserva.id_cancha.id_recinto
        try:
            reserva.full_clean()
            reserva.save()
            messages.success(
                self.request,
                f'Reserva confirmada para {reserva.fecha_reserva} de {reserva.hora_inicio} a {reserva.hora_fin}.',
            )
            return redirect('mis_reservas')
        except Exception as e:
            messages.error(self.request, f'Error al crear reserva: {str(e)}')
            return self.render_to_response(self.get_context_data(form=form))


class MisReservasView(LoginRequiredMixin, TemplateView):
    template_name = 'canchas/mis_reservas.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        reservas = Reserva.objects.filter(
            id_usuario=self.request.user
        ).select_related('id_cancha', 'id_recinto').order_by('-fecha_reserva', '-hora_inicio')
        ahora = timezone.now()
        reservas_futuras = reservas.filter(fecha_reserva__gte=ahora.date()).exclude(estado='cancelada')
        reservas_pasadas = reservas.filter(
            DJQ(fecha_reserva__lt=ahora.date()) | DJQ(estado='cancelada')
        )[:20]
        ctx.update({
            'reservas_futuras': reservas_futuras,
            'reservas_pasadas': reservas_pasadas,
        })
        return ctx


class CancelarReservaView(LoginRequiredMixin, TemplateView):
    template_name = 'canchas/cancelar_reserva.html'

    def dispatch(self, request, *args, **kwargs):
        self.reserva = get_object_or_404(
            Reserva, id_reserva=kwargs['reserva_id'], id_usuario=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['reserva'] = self.reserva
        return ctx

    def post(self, request, *args, **kwargs):
        reserva = self.reserva
        if reserva.estado == 'cancelada':
            messages.warning(request, 'Esta reserva ya está cancelada.')
            return redirect('mis_reservas')
        reserva.estado = 'cancelada'
        reserva.save()
        messages.success(request, 'Reserva cancelada exitosamente.')
        return redirect('mis_reservas')


class ApiHorariosDisponiblesView(View):

    def get(self, request):
        cancha_id = request.GET.get('cancha_id')
        if not cancha_id:
            return JsonResponse({'error': 'cancha_id requerido'}, status=400)

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
        horarios_formateados = [{
            'hora_inicio': slot['hora_inicio'].strftime('%H:%M'),
            'hora_fin': slot['hora_fin'].strftime('%H:%M'),
        } for slot in horarios]

        return JsonResponse({
            'cancha': cancha.nombre,
            'fecha': fecha_str,
            'horarios': horarios_formateados
        })


class MisCanchasAdminView(GestionCanchasMixin, TemplateView):
    """Panel para administradores de recinto: sus canchas, enlaces a edición y horarios."""
    template_name = 'canchas/mis_canchas_admin.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        recintos = list(
            recintos_para_dropdown_cancha(user).select_related('id_localidad').order_by('nombre')
        )
        recinto_ids = [r.pk for r in recintos]
        canchas_qs = (
            Cancha.objects.filter(id_recinto__in=recinto_ids)
            .select_related('id_recinto', 'id_recinto__id_localidad')
            .annotate(n_horarios_activos=Count('horarios', filter=DJQ(horarios__activo=True)))
            .order_by('nombre')
        )
        por_recinto = defaultdict(list)
        for cancha in canchas_qs:
            por_recinto[cancha.id_recinto_id].append(cancha)
        ctx['bloques_recinto'] = [
            {'recinto': r, 'canchas': por_recinto[r.pk]}
            for r in recintos
        ]
        ctx['total_canchas'] = len(canchas_qs)
        return ctx


lista_canchas = ListaCanchasView.as_view()
lista_recintos = ListaRecintosView.as_view()
crear_recinto = CrearRecintoView.as_view()
editar_recinto = EditarRecintoView.as_view()
crear_cancha = CrearCanchaView.as_view()
editar_cancha = EditarCanchaView.as_view()
disponibilidad_cancha = DisponibilidadCanchaView.as_view()
gestionar_horarios_cancha = GestionarHorariosCanchaView.as_view()
crear_reserva = CrearReservaView.as_view()
mis_reservas = MisReservasView.as_view()
cancelar_reserva = CancelarReservaView.as_view()
api_horarios_disponibles = ApiHorariosDisponiblesView.as_view()
mis_canchas_admin = MisCanchasAdminView.as_view()
