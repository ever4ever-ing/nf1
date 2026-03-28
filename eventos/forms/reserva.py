from django import forms

from ..models import Reserva


class ReservaForm(forms.ModelForm):
    fecha_reserva = forms.DateField(
        label='Fecha',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = Reserva
        fields = ['id_cancha', 'fecha_reserva', 'hora_inicio', 'hora_fin', 'notas']
        widgets = {
            'id_cancha': forms.Select(attrs={'class': 'form-select', 'id': 'id_cancha'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'step': '1800'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'step': '1800'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones (opcional)'}),
        }
        labels = {
            'id_cancha': 'Cancha',
            'fecha_reserva': 'Fecha',
            'hora_inicio': 'Hora de Inicio',
            'hora_fin': 'Hora de Fin',
            'notas': 'Notas'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'fecha_reserva' in kwargs['initial']:
            fecha_str = kwargs['initial']['fecha_reserva']
            if ' ' in fecha_str:
                from datetime import datetime
                dt = datetime.fromisoformat(fecha_str)
                self.fields['fecha_reserva'].initial = dt.date()
