from django import forms

from ..models import MiembroEquipo


class AsignarNumeroCamisetaForm(forms.ModelForm):
    class Meta:
        model = MiembroEquipo
        fields = ['numero_camiseta']
        widgets = {
            'numero_camiseta': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 99, 'placeholder': 'Número'}),
        }
