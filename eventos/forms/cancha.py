from django import forms

from ..models import Cancha


class CanchaForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = ['nombre', 'id_recinto', 'tipo', 'max_jugadores']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la cancha'}),
            'id_recinto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Fútbol 11, Fútbol 7, Fútbol 5'}),
            'max_jugadores': forms.NumberInput(attrs={'class': 'form-control', 'min': '2', 'max': '100'}),
        }
        labels = {
            'nombre': 'Nombre de la Cancha',
            'id_recinto': 'Recinto',
            'tipo': 'Tipo de Cancha',
            'max_jugadores': 'Máximo de jugadores',
        }
