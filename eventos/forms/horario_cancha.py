from django import forms

from ..models import HorarioCancha


class HorarioCanchaForm(forms.ModelForm):
    """Pasá `cancha=` al crear el formulario: la validación del modelo necesita id_cancha antes de is_valid()."""

    def __init__(self, *args, cancha=None, **kwargs):
        super().__init__(*args, **kwargs)
        if cancha is not None:
            self.instance.id_cancha = cancha

    class Meta:
        model = HorarioCancha
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'activo']
        widgets = {
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'dia_semana': 'Día de la Semana',
            'hora_inicio': 'Hora de Apertura',
            'hora_fin': 'Hora de Cierre',
            'activo': 'Activo'
        }
