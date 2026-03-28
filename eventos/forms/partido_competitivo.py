from django import forms

from ..models import PartidoCompetitivo


class PartidoCompetitivoForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = PartidoCompetitivo
        fields = ['nombre', 'descripcion', 'id_equipo_visitante', 'id_cancha', 'id_localidad', 'lugar', 'fecha_hora']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del partido'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del partido...'}),
            'id_equipo_visitante': forms.Select(attrs={'class': 'form-select'}),
            'id_cancha': forms.Select(attrs={'class': 'form-select'}),
            'id_localidad': forms.Select(attrs={'class': 'form-select'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicación del partido'}),
        }
