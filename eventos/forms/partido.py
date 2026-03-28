from datetime import datetime

from django import forms
from django.utils import timezone

from ..models import Cancha, Partido


class PartidoCrearForm(forms.ModelForm):
    """Crear partido: lugar, localidad, cupo y fecha/hora salen de la cancha y la reserva."""

    fecha_reserva = forms.DateField(
        required=True,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'hidden', 'id': 'id_fecha_reserva'},
        ),
    )
    id_cancha_reserva = forms.ModelChoiceField(
        queryset=Cancha.objects.select_related('id_recinto__id_localidad').all(),
        required=True,
        label='Cancha',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_cancha_reserva'}),
    )
    hora_inicio_reserva = forms.TimeField(
        required=True,
        label='Hora inicio',
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'step': '1800'}),
    )
    hora_fin_reserva = forms.TimeField(
        required=True,
        label='Hora fin',
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'step': '1800'}),
    )

    class Meta:
        model = Partido
        fields = ['descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe tu partido: nivel, reglas, qué llevar, etc.',
                'rows': 4,
            }),
        }
        labels = {
            'descripcion': 'Descripción',
        }

    def clean(self):
        cleaned_data = super().clean()
        cancha = cleaned_data.get('id_cancha_reserva')
        fecha_r = cleaned_data.get('fecha_reserva')
        hora_inicio = cleaned_data.get('hora_inicio_reserva')
        hora_fin = cleaned_data.get('hora_fin_reserva')

        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            self.add_error('hora_fin_reserva', 'La hora de fin debe ser posterior a la hora de inicio.')

        if fecha_r and hora_inicio and hora_fin and hora_inicio < hora_fin:
            naive = datetime.combine(fecha_r, hora_inicio)
            cleaned_data['fecha_inicio'] = timezone.make_aware(naive, timezone.get_current_timezone())
        else:
            cleaned_data['fecha_inicio'] = None

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('id_cancha_reserva', 'fecha_reserva', 'hora_inicio_reserva', 'hora_fin_reserva'):
            if name in self.initial and self.initial[name] is not None:
                self.fields[name].initial = self.initial[name]

    def save(self, commit=True):
        instance = super().save(commit=False)
        cancha = self.cleaned_data['id_cancha_reserva']
        recinto = cancha.id_recinto
        instance.lugar = f'{cancha.nombre} — {recinto.nombre}'
        instance.id_localidad = recinto.id_localidad
        instance.max_jugadores = cancha.max_jugadores
        instance.fecha_inicio = self.cleaned_data.get('fecha_inicio')
        if commit:
            instance.save()
        return instance


class PartidoEditForm(forms.ModelForm):
    """Editar partido: mantiene fecha/hora en un solo campo (sin flujo de reserva en este formulario)."""

    fecha_inicio = forms.DateTimeField(
        label='Fecha y Hora',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'placeholder': 'Selecciona fecha y hora',
        }),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Partido
        fields = ['lugar', 'fecha_inicio', 'id_localidad', 'max_jugadores', 'descripcion']
        widgets = {
            'lugar': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Cancha Municipal, Estadio Central',
            }),
            'id_localidad': forms.Select(attrs={'class': 'form-select'}),
            'max_jugadores': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2',
                'max': '100',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe tu partido: nivel, reglas, qué llevar, etc.',
                'rows': 4,
            }),
        }
        labels = {
            'lugar': 'Lugar del Partido',
            'fecha_inicio': 'Fecha y Hora',
            'id_localidad': 'Localidad',
            'max_jugadores': 'Máximo de Jugadores',
            'descripcion': 'Descripción',
        }
