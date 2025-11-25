from django import forms
from .models import Recinto, Cancha
from eventos.models import Localidad


class RecintoForm(forms.ModelForm):
    class Meta:
        model = Recinto
        fields = ['nombre', 'direccion', 'id_localidad']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del recinto'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa',
                'rows': 3
            }),
            'id_localidad': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'nombre': 'Nombre del Recinto',
            'direccion': 'Dirección',
            'id_localidad': 'Localidad'
        }


class CanchaForm(forms.ModelForm):
    class Meta:
        model = Cancha
        fields = ['nombre', 'id_recinto', 'tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la cancha'
            }),
            'id_recinto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Fútbol 11, Fútbol 7, Fútbol 5'
            }),
        }
        labels = {
            'nombre': 'Nombre de la Cancha',
            'id_recinto': 'Recinto',
            'tipo': 'Tipo de Cancha'
        }
