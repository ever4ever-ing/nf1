from django import forms

from ..models import PartidoCompetitivo


class ActualizarResultadoForm(forms.ModelForm):
    class Meta:
        model = PartidoCompetitivo
        fields = ['goles_local', 'goles_visitante', 'estado']
        widgets = {
            'goles_local': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'goles_visitante': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
